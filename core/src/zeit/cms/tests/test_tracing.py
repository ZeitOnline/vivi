import opentelemetry.trace
import zeit.cms.testing
import zeit.cms.tracing


class TracerSmokeTest(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        self.set_tracer_provider(opentelemetry.sdk.trace.TracerProvider())

    def tearDown(self):
        self.set_tracer_provider(None)
        super().tearDown()

    def set_tracer_provider(self, provider):
        opentelemetry.trace._TRACER_PROVIDER_SET_ONCE._done = False  # sigh
        opentelemetry.trace.set_tracer_provider(provider)

    def test_otlp_tracer_can_be_instantiated(self):
        provider = zeit.cms.tracing.OpenTelemetryTracerProvider(
            'zeit.cms', 'testing', 'testing', 'localhost', 'localhost:1234')
        opentelemetry.trace.set_tracer_provider(provider)
        with self.assertNothingRaised():
            zeit.cms.tracing.default_tracer()

    def test_start_span_yields_nonrecording_according_to_context(self):
        span = zeit.cms.tracing.start_span('test.tracing', 'example')
        self.assertIsInstance(span, opentelemetry.trace.NonRecordingSpan)

        context = opentelemetry.context.set_value('test.tracing', 42)
        token = opentelemetry.context.attach(context)
        span = zeit.cms.tracing.start_span('test.tracing', 'example')
        self.assertEqual(42, span.attributes['SampleRate'])
        opentelemetry.context.detach(token)
