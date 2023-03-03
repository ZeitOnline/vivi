from ZEO.asyncio.client import ClientRunner, Protocol
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
import functools
import opentelemetry.trace


class ZEOInstrumentor(BaseInstrumentor):

    def instrumentation_dependencies(self):
        return ("ZEO ~= 5.0",)

    def _instrument(self, **kw):
        tracer = opentelemetry.trace.get_tracer(
            __name__, tracer_provider=kw.get("tracer_provider"))

        wrapped_setup_delegation = ClientRunner.setup_delegation

        @functools.wraps(wrapped_setup_delegation)
        def instrumented_setup_delegation(self, *args, **kw):
            wrapped_setup_delegation(self, *args, **kw)
            wrapped_call = self._ClientRunner__call

            def instrumented_call(method, *args, **kw):
                operation = method.__name__.removesuffix('_threadsafe')
                if operation in ['call', 'call_async']:
                    operation = args[0]
                    traceargs = args[1]
                else:
                    traceargs = args
                if operation in [
                        'tpc_begin', 'vote', 'tpc_finish', 'tpc_abort']:
                    tid = str(traceargs[0])
                else:
                    tid = ''

                with tracer.start_as_current_span(
                        'ZEO ' + operation, attributes={
                            'type': 'client', 'db.transaction': tid}):
                    return wrapped_call(method, *args, **kw)

            self._ClientRunner__call = instrumented_call

        instrumented_setup_delegation.otel_zeo_instrumented = True
        ClientRunner.setup_delegation = instrumented_setup_delegation

        wrapped_connect = Protocol.connect

        @functools.wraps(wrapped_connect)
        def instrumented_connect(self):
            span = tracer.start_as_current_span('ZEO connect', attributes={
                'type': 'client', 'zeo.server': str(self.addr)})
            span.__enter__()
            wrapped_connect(self)
            self._connecting.add_done_callback(
                lambda x: span.__exit__(None, None, None))

        instrumented_connect.otel_zeo_instrumented = True
        Protocol.connect = instrumented_connect

    def _uninstrument(self, **kw):
        for cls, names in {
                Protocol: ['connect'],
                ClientRunner: ['setup_delegation']}:
            for name in names:
                func = getattr(cls, name)
                if not getattr(func, 'otel_zeo_instrumented', False):
                    continue
                original = func.__wrapped__
                setattr(cls, name, original)
