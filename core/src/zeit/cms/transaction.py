import functools

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from transaction import Transaction
import opentelemetry.trace


class TransactionInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self):
        return ('transaction >= 3.0',)

    def _instrument(self, **kw):
        tracer = opentelemetry.trace.get_tracer(__name__, tracer_provider=kw.get('tracer_provider'))

        # commit
        wrapped_before_commit = Transaction._callBeforeCommitHooks

        @functools.wraps(wrapped_before_commit)
        def instrumented_before_commit(self, *args, **kw):
            self._span_commit = tracer.start_as_current_span('transaction commit')
            self._span_commit.__enter__()
            try:
                wrapped_before_commit(self, *args, **kw)
            except Exception as e:
                self._span_commit.__exit__(type(e), e, e.__traceback__)
                del self._span_commit
                raise

        instrumented_before_commit.otel_instrumented = True
        Transaction._callBeforeCommitHooks = instrumented_before_commit

        wrapped_after_commit = Transaction._callAfterCommitHooks

        @functools.wraps(wrapped_after_commit)
        def instrumented_after_commit(self, *args, **kw):
            wrapped_after_commit(self, *args, **kw)
            if hasattr(self, '_span_commit'):
                self._span_commit.__exit__(None, None, None)
                del self._span_commit

        instrumented_after_commit.otel_instrumented = True
        Transaction._callAfterCommitHooks = instrumented_after_commit

        # abort
        wrapped_before_abort = Transaction._callBeforeAbortHooks

        @functools.wraps(wrapped_before_abort)
        def instrumented_before_abort(self, *args, **kw):
            self._span_abort = tracer.start_as_current_span('transaction abort')
            self._span_abort.__enter__()
            wrapped_before_abort(self, *args, **kw)

        instrumented_before_abort.otel_instrumented = True
        Transaction._callBeforeAbortHooks = instrumented_before_abort

        wrapped_after_abort = Transaction._callAfterAbortHooks

        @functools.wraps(wrapped_after_abort)
        def instrumented_after_abort(self, *args, **kw):
            wrapped_after_abort(self, *args, **kw)
            if hasattr(self, '_span_abort'):
                self._span_abort.__exit__(None, None, None)
                del self._span_abort

        instrumented_after_abort.otel_instrumented = True
        Transaction._callAfterAbortHooks = instrumented_after_abort

    def _uninstrument(self, **kw):
        for cls, names in {
            Transaction: [
                '_callBeforeCommitHooks',
                '_callAfterCommitHooks',
                '_callBeforeAbortHooks',
                '_callAfterAbortHooks',
            ]
        }:
            for name in names:
                func = getattr(cls, name)
                if not getattr(func, 'otel_instrumented', False):
                    continue
                original = func.__wrapped__
                setattr(cls, name, original)
