import contextlib
import importlib.metadata
import os
import re
import socket
import time

from cryptography.fernet import Fernet
from opentelemetry.instrumentation.utils import http_status_to_status_code
from opentelemetry.trace.status import Status
import opentelemetry.trace
import zope.interface

import zeit.cms.interfaces


try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import Tracer, TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope
except ImportError:
    TracerProvider = object
    Tracer = object


class OpenTelemetryTracerProvider(TracerProvider):
    def __init__(
        self, service_name, service_version, environment, hostname, otlp_url, headers=None
    ):
        # see <specification/resource/semantic_conventions/README.md>
        resource = Resource.create(
            {
                'service.name': service_name,
                'service.version': service_version,
                'service.namespace': environment,
                'service.instance.id': hostname,
            }
        )
        super().__init__(resource=resource)

        self.otlp_url = otlp_url
        self.headers = headers
        self.initialized = False

    def initialize(self):
        """Defer starting thread *after* gunicorn has forked its workers."""
        self.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=self.otlp_url,
                    insecure=not self.otlp_url.startswith('https'),
                    headers=self.headers,
                )
            )
        )
        self.initialized = True

    # Even though TracerProvider declares kwargs,
    # opentelemetry.trace.get_tracer() passes them as positional, so we cannot
    # use `**kw` here, sigh.
    def get_tracer(self, name, version=None, schema_url=None):
        if not name:
            name = __name__
        return DelayedInitializationTracer(self, name, version, schema_url)


class DelayedInitializationTracer(Tracer):
    def __init__(self, provider, name, version, schema_url):
        super().__init__(
            provider.sampler,
            provider.resource,
            provider._active_span_processor,
            provider.id_generator,
            None,  # InstrumentationInfo was replaced by InstrumentationScope
            provider._span_limits,
            InstrumentationScope(name, version, schema_url),
        )
        self.provider = provider

    def start_as_current_span(self, *args, **kw):
        if not self.provider.initialized:
            self.provider.initialize()
        return super().start_as_current_span(*args, **kw)

    def start_span(self, *args, **kw):
        if not self.provider.initialized:
            self.provider.initialize()
        return super().start_span(*args, **kw)


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
def default_tracer():
    """Clients may also call get_tracer() themselves, even at import time
    before the TracerProvider is configured, as opentelemetry-api has a proxy
    system that delegates to the real TracerProvider when start_span is called.
    (If no TracerProvider is configured, opentelemetry-api automatically
    provides a noop implementation, which is handy e.g. for tests)

    Benefits of using a utility in our code instead of the opentelemetry API:
    * It fits the established pattern of how we handle dependency injection
    * Overriding the utility registration is a good extension point for where
      to perform the TracerProvider configuration
    * We save the (small) impact of constructing a new Tracer object each time
    * We don't really care about the `library.name` field that's populated by
      the argument to get_tracer().
    """
    return opentelemetry.trace.get_tracer(__name__)


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
def tracer_from_product_config():
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    import zope.app.appsetup.product

    from zeit.cms.relstorage import RelStorageInstrumentor

    hostname = socket.gethostname()
    # We don't want the FQDN and date suffix.
    hostname = re.split('([-]{1}[0-9]{3,})|(.zeit){1}', hostname)[0]

    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    provider = zeit.cms.tracing.OpenTelemetryTracerProvider(
        'vivi',
        importlib.metadata.version('vivi.core'),
        config['environment'],
        hostname,
        config['otlp-url'],
        headers={
            'x-honeycomb-team': config['honeycomb-apikey'],
            'x-honeycomb-dataset': config['honeycomb-dataset'],
        },
    )
    opentelemetry.trace.set_tracer_provider(provider)

    RequestsInstrumentor().instrument(tracer_provider=provider)
    RelStorageInstrumentor().instrument(tracer_provider=provider)

    return default_tracer()


@zope.interface.implementer(zeit.cms.interfaces.ITracer)
def stdout_tracer():
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    opentelemetry.trace.set_tracer_provider(provider)
    return default_tracer()


@zope.interface.implementer(zeit.cms.interfaces.IMetrics)
def prometheus_metrics():
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider

    provider = MeterProvider([PrometheusMetricReader(prefix='')])
    opentelemetry.metrics.set_meter_provider(provider)


def start_span(module, *args, **kw):
    samplerate = opentelemetry.context.get_value(module)
    if samplerate:
        tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
        span = tracer.start_span(*args, **kw)
        span.set_attribute('SampleRate', samplerate)
        return span
    else:
        return opentelemetry.trace.INVALID_SPAN


@contextlib.contextmanager
def use_span(module, *args, **kw):
    span = start_span(module, *args, **kw)
    with opentelemetry.trace.use_span(span, end_on_exit=True) as span:
        yield span


def record_span(span, status_code, body):
    span.set_attribute('http.status_code', status_code)
    span.set_attribute('http.content', body)
    span.set_status(Status(http_status_to_status_code(status_code)))


def anonymize(value):
    if not value:
        return ''
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    key = config.get('honeycomb-personal-data-key')
    if not key:  # Better to send irreversibly encrypted data than cleartext.
        key = Fernet.generate_key()
    ts = config.get('honeycomb-personal-data-ts')
    if ts:
        ts = int(ts)
    else:
        ts = int(time.time())
    iv = config.get('honeycomb-personal-data-iv')
    if iv:
        iv = iv.encode('utf-8')
    else:
        iv = os.urandom(16)
    return Fernet(key)._encrypt_from_parts(value.encode('utf-8'), ts, iv).decode('ascii')


class TestTrace:
    def __init__(self, exporter):
        self._exporter = exporter

    @property
    def spans(self):
        return self._exporter.get_finished_spans()

    def __getitem__(self, name):
        for span in self.spans:
            if span.name == name:
                return span
        raise KeyError(name)

    @staticmethod
    def provider():
        provider = TracerProvider()
        exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        return provider, exporter


@contextlib.contextmanager
def captrace():
    provider, exporter = TestTrace.provider()
    _testing_set_tracer_provider(provider)
    yield TestTrace(exporter)
    exporter.clear()
    _testing_set_tracer_provider(None)


def _testing_set_tracer_provider(provider):
    opentelemetry.trace._TRACER_PROVIDER_SET_ONCE._done = False  # sigh
    opentelemetry.trace.set_tracer_provider(provider)
