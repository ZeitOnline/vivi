import opentelemetry.trace
import zeit.cms.testing
import zeit.cms.tracing


class TracerSmokeTest(zeit.cms.testing.ZeitCmsTestCase):

    def tearDown(self):
        opentelemetry.trace._TRACER_PROVIDER_SET_ONCE._done = False  # sigh
        opentelemetry.trace.set_tracer_provider(None)
        super().tearDown()

    def test_otlp_tracer_can_be_instantiated(self):
        provider = zeit.cms.tracing.OpenTelemetryTracerProvider(
            'zeit.cms', 'testing', 'testing', 'localhost', 'localhost:1234')
        opentelemetry.trace.set_tracer_provider(provider)
        with self.assertNothingRaised():
            zeit.cms.tracing.default_tracer()
