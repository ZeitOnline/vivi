import functools
import logging
import random

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from ZEO.asyncio.client import ClientRunner, Protocol
import opentelemetry.trace
import zope.app.appsetup.product


class ZEOInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return ('ZEO ~= 5.4',)

    def _instrument(self, **kw):
        tracer = opentelemetry.trace.get_tracer(__name__, tracer_provider=kw.get('tracer_provider'))

        wrapped_setup_delegation = ClientRunner.setup_delegation

        @functools.wraps(wrapped_setup_delegation)
        def instrumented_setup_delegation(self, *args, **kw):
            wrapped_setup_delegation(self, *args, **kw)
            wrapped_call = self.io_call

            def instrumented_call(method, *args, **kw):
                operation = method.__name__.removesuffix('_threadsafe')
                if operation in ['call', 'call_async']:
                    operation = args[0]
                    traceargs = args[1]
                else:
                    traceargs = args
                if operation in ['tpc_begin', 'vote', 'tpc_finish', 'tpc_abort']:
                    tid = str(traceargs[0])
                else:
                    tid = ''

                if logging.getLogger(__name__).isEnabledFor(logging.DEBUG):
                    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
                    with tracer.start_as_current_span(
                        'ZEO ' + operation,
                        attributes={
                            'span.kind': 'client',
                            'db.transaction': tid,
                            'SampleRate': config['samplerate-zeo'],
                        },
                    ):
                        return wrapped_call(method, *args, **kw)
                else:
                    return wrapped_call(method, *args, **kw)

            self.io_call = instrumented_call

        instrumented_setup_delegation.otel_zeo_instrumented = True
        ClientRunner.setup_delegation = instrumented_setup_delegation

        wrapped_connect = Protocol.connect

        @functools.wraps(wrapped_connect)
        def instrumented_connect(self):
            span = tracer.start_as_current_span(
                'ZEO connect', attributes={'type': 'client', 'zeo.server': str(self.addr)}
            )
            span.__enter__()
            wrapped_connect(self)
            self._connecting.add_done_callback(lambda x: span.__exit__(None, None, None))

        instrumented_connect.otel_zeo_instrumented = True
        Protocol.connect = instrumented_connect

    def _uninstrument(self, **kw):
        for cls, names in {Protocol: ['connect'], ClientRunner: ['setup_delegation']}:
            for name in names:
                func = getattr(cls, name)
                if not getattr(func, 'otel_zeo_instrumented', False):
                    continue
                original = func.__wrapped__
                setattr(cls, name, original)


def apply_samplerate(*args, **kw):
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    zeo = logging.getLogger(__name__)
    # XXX It would be cleaner to use the otel context to transmit this
    # information, but that's mechanically difficult due to attach/detach API.
    if random.random() <= 1 / int(config.get('samplerate-zeo', 1)):
        zeo.setLevel(logging.DEBUG)
    else:
        zeo.setLevel(logging.NOTSET)
