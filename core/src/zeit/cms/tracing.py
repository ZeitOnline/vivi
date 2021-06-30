import opentelemetry.trace
import zeit.cms.interfaces
import zope.interface

try:
    from opentelemetry.sdk.trace import Tracer, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.util.instrumentation import InstrumentationInfo
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter)
except ImportError:
    TracerProvider = object
    Tracer = object


class OpenTelemetryTracerProvider(TracerProvider):

    def __init__(self, service_name, service_version, environment, hostname,
                 otlp_url):
        # see <specification/resource/semantic_conventions/README.md>
        resource = Resource.create({
            'service.name': service_name,
            'service.version': service_version,
            'service.namespace': environment,
            'service.instance.id': hostname,
        })
        super().__init__(resource=resource)

        self.otlp_url = otlp_url
        self.initialized = False

    def initialize(self):
        """Defer starting thread *after* gunicorn has forked its workers."""
        self.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(
                endpoint=self.otlp_url,
                insecure=not self.otlp_url.startswith('https'))))
        self.initialized = True

    def get_tracer(self, name=None, version=''):
        if not name:
            name = __name__
        return DelayedInitializationTracer(self, name, version)


class DelayedInitializationTracer(Tracer):

    def __init__(self, provider, name, version):
        super().__init__(
            provider.sampler, provider.resource,
            provider._active_span_processor, provider.id_generator,
            InstrumentationInfo(name, version), provider._span_limits)
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
    """Clients may also call get_tracer() themselves, even at import time before
    the TracerProvider is configured, as opentelemetry-api has a proxy system
    that delegates to the real TracerProvider when start_span is called.
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
