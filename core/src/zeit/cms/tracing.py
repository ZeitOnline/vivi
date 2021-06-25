from unittest import mock
import contextlib
import logging
import random
import sys
import traceback
import uuid
import zeit.cms.interfaces
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
class FakeTracer(object):

    def start_trace(self, trace_id=None, parent_id=None):
        result = mock.Mock()
        result.id = str(uuid.uuid4())
        # XXX This API is beeline specific
        result.trace_id = trace_id
        result.parent_id = parent_id
        return result

    def end_trace(self, trace, **kw):
        pass

    def start_span(self, typ, name, **kw):
        pass

    def add_span_data(self, span, **kw):
        pass

    def end_span(self, span, exc_info=()):
        pass

    @contextlib.contextmanager
    def span(self, typ, name, **kw):
        span = self.start_span(typ, name, **kw)
        exc_info = []
        try:
            yield span
        except Exception:
            exc_info[:] = sys.exc_info()
            raise
        finally:
            self.end_span(span, exc_info)


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
class APMTracer(FakeTracer):

    def __init__(self, service_name, service_version, environment, hostname,
                 apm_url, apm_token):
        # Disable APM metrics reporting, we use Prometheus for those.
        elasticapm.metrics.base_metrics.MetricsRegistry.start_thread = (
            lambda *args, **kw: None)

        self.client = elasticapm.Client(
            server_url=apm_url,
            secret_token=apm_token,
            instrument=False,
            transactions_ignore_patterns=['^health_check$'],
            service_name=service_name,
            service_node_name=hostname,
            service_version=service_version,
            hostname=hostname,
            environment=environment)

    def start_trace(self, trace_id=None, parent_id=None):
        # elastic APM can push config updates to clients (e.g. for
        # transaction_sample_rate), so we use that, not a X-B3-Sampled header.
        # Copied from elasticapm.traces.Tracer.begin_transaction().
        config = self.client.config
        is_sampled = (config.transaction_sample_rate == 1.0 or
                      config.transaction_sample_rate > random.random())
        if parent_id:
            parent_span = elasticapm.utils.disttracing.TraceParent(
                version=elasticapm.conf.constants.TRACE_CONTEXT_VERSION,
                trace_id=trace_id,
                span_id=parent_id,
                trace_options=elasticapm.utils.disttracing.TracingOptions(
                    recorded=is_sampled))
        else:
            parent_span = None
        return self.client.begin_transaction('http_server', parent_span)

    def end_trace(self, trace, name, status_code, **kw):
        self.client.end_transaction(name, status_code)

    def start_span(self, typ, name, **kw):
        span = elasticapm.capture_span(name, typ)
        span.__enter__()
        span.labels = kw
        return span

    def add_span_data(self, span, **kw):
        span.labels.update(kw)

    def end_span(self, span, exc_info=()):
        span.__exit__(*exc_info)


try:
    import elasticapm
except ImportError:
    APMTracer = FakeTracer  # noqa


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
class HoneyTracer(FakeTracer):

    def __init__(self, service_name, service_version, environment, hostname,
                 apikey, dataset, sample_rate=1):
        self.apikey = apikey
        self.dataset = dataset
        self.service_name = service_name
        self.sample_rate = sample_rate

        self.context = {
            'meta.environment': environment,
            'meta.local_hostname': hostname,
            'meta.service': service_name,
            'meta.version': service_version,
        }
        self._initialized = False

    def _initialize(self):
        """beeline starts a sending thread, which we have to defer until *after*
        gunicorn has forked its workers."""
        beeline.init(
            writekey=self.apikey, dataset=self.dataset,
            service_name=self.service_name, presend_hook=self.prepare,
            sample_rate=self.sample_rate)
        self._initialized = True

    def prepare(self, fields):
        fields.update(self.context)

    def start_trace(self, trace_id=None, parent_id=None):
        if not self._initialized:
            self._initialize()
        return beeline.start_trace(trace_id=trace_id, parent_span_id=parent_id)

    def end_trace(self, trace, **kw):
        kw.setdefault('meta.name', 'unknown')
        kw.setdefault('resp.status_code', 599)
        beeline.add_context(kw)
        beeline.finish_trace(trace)

    def start_span(self, typ, name, **kw):
        span = beeline.start_span(
            context={'meta.type': typ, 'meta.name': name})
        self.add_span_data(span, **kw)
        return span

    def add_span_data(self, span, **kw):
        beeline.add_context(kw)

    def end_span(self, span, exc_info=()):
        if exc_info and exc_info[0]:
            beeline.add_context({
                'error': str(exc_info[0]),
                'error_detail': str(exc_info[1])
            })
        beeline.finish_span(span)


try:
    import beeline
except ImportError:
    HoneyTracer = FakeTracer  # noqa


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
class OpenTelemetryTracer(FakeTracer):

    def __init__(self, service_name, service_version, environment, hostname,
                 otlp_url):
        self.provider = opentelemetry.sdk.trace.TracerProvider(
            # see <specification/resource/semantic_conventions/README.md>
            resource=opentelemetry.sdk.resources.Resource.create({
                'service.name': service_name,
                'service.version': service_version,
                'service.namespace': environment,
                'service.instance.id': hostname,
            }))
        opentelemetry.trace.set_tracer_provider(self.provider)
        self.tracer = self.provider.get_tracer('zeit.cms.tracing')

        self.otlp_url = otlp_url
        self._initialized = False

    def _initialize(self):
        """Start sending thread *after* gunicorn has forked its workers."""
        self.provider.add_span_processor(
            BatchSpanProcessor(otlp.OTLPSpanExporter(
                endpoint=self.otlp_url,
                insecure=not self.otlp_url.startswith('https'))))
        self._initialized = True

    def start_trace(self, trace_id=None, parent_id=None):
        if not self._initialized:
            self._initialize()

        try:  # The opentelemetry libraries insist on IDs being ints.
            int_trace_id = int(trace_id, 16)
            int_parent_id = int(parent_id, 16)
        except ValueError:
            pass
        else:
            # Like opentelemetry.trace.propagation.tracecontext:extract()
            parent = opentelemetry.trace.NonRecordingSpan(SpanContext(
                int_trace_id, int_parent_id, is_remote=True,
                trace_flags=TraceFlags(TraceFlags.SAMPLED)))
            opentelemetry.context.attach(
                opentelemetry.trace.set_span_in_context(parent))

        span = self.tracer.start_span('unknown')
        # Like opentelemetry.trace.use_span(span)
        span.context_token = opentelemetry.context.attach(
            opentelemetry.trace.set_span_in_context(span))
        # XXX Emulate beeline API
        span.id = opentelemetry.trace.format_span_id(
            span.get_span_context().span_id)
        span.trace_id = trace_id
        span.parent_id = parent_id
        return span

    def end_trace(self, span, **kw):
        name = kw.pop('name')
        if name is not None:
            span.update_name(name)
        span.set_attributes(kw)
        opentelemetry.context.detach(span.context_token)
        span.end()

    def start_span(self, typ, name, **kw):
        return self.tracer.start_span(name, attributes=kw)

    def add_span_data(self, span, **kw):
        span.set_attributes(kw)

    def end_span(self, span, exc_info=()):
        if exc_info and exc_info[0]:
            # see <specification/trace/semantic_conventions/exceptions.md>
            span.set_attributes({
                'exception.type': str(exc_info[0]),
                'exception.message': str(exc_info[1]),
                'exception.stacktrace': traceback.format_tb(exc_info[2]),
            })
        span.end()


try:
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import SpanContext, TraceFlags
    import opentelemetry.context
    import opentelemetry.trace
    import opentelemetry.exporter.otlp.proto.grpc.trace_exporter as otlp
    import opentelemetry.sdk.trace
    import opentelemetry.sdk.resources
except ImportError:
    OpenTelemetryTracer = FakeTracer  # noqa
