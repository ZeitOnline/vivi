import opentelemetry.trace

from zeit.cms.tracing import _testing_set_tracer_provider as set_tracer_provider
import zeit.cms.testing
import zeit.cms.tracing


class TracerSmokeTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        set_tracer_provider(opentelemetry.sdk.trace.TracerProvider())

    def tearDown(self):
        set_tracer_provider(None)
        super().tearDown()

    def test_otlp_tracer_can_be_instantiated(self):
        provider = zeit.cms.tracing.OpenTelemetryTracerProvider(
            'zeit.cms', 'testing', 'testing', 'localhost', 'localhost:1234'
        )
        set_tracer_provider(provider)
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
