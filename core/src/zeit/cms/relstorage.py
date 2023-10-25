from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from perfmetrics.metric import _AbstractMetricImpl as MetricImpl
from relstorage.zodburi_resolver import RelStorageURIResolver, Resolver
import ZODB.serialize
import functools
import logging
import opentelemetry.trace
import perfmetrics._util
import zeit.cms.cli
import zodburi
import zope.app.appsetup.product


class PsqlServiceResolver(Resolver):

    def __call__(self, parsed_uri, kw):
        def factory(options):
            from relstorage.adapters.postgresql import PostgreSQLAdapter
            return PostgreSQLAdapter(
                dsn='service=' + parsed_uri.hostname, options=options)
        return factory, kw


psql_resolver = RelStorageURIResolver(PsqlServiceResolver())


def zodbpack():
    settings = zeit.cms.cli.parse_paste_ini()
    storage_factory, db_kw = zodburi.resolve_uri(settings['zodbconn.uri'])
    storage = storage_factory()
    # We use keep_history=False, so we run pack only for garbage collection
    timestamp = None
    storage.pack(timestamp, ZODB.serialize.referencesf)
    storage.close()


class RelStorageInstrumentor(BaseInstrumentor):
    """The relstorage codebase is already instrumented for statsd via the
    `perfmetrics` library, so we hook into that to trace relevant functions.
    """

    def instrumentation_dependencies(self):
        return ("relstorage ~= 3.5",)

    def _instrument(self, **kw):
        tracer = opentelemetry.trace.get_tracer(
            __name__, tracer_provider=kw.get("tracer_provider"))

        if not perfmetrics._util.PURE_PYTHON:
            logging.getLogger(__name__).warning(
                'perfmetrics loaded C extensions, skipping instrumentation')
            return

        wrapped_call = MetricImpl.__call__

        @functools.wraps(wrapped_call)
        def instrumented_call(self, *args, **kw):
            # XXX Reuse zeo sampling, move it here when we remove zeo.
            if logging.getLogger('zeit.cms.zeo').isEnabledFor(logging.DEBUG):
                config = zope.app.appsetup.product.getProductConfiguration(
                    'zeit.cms')
                operation = self.stat_name or self._compute_stat(args)
                with tracer.start_as_current_span(
                        operation, attributes={
                            'span.kind': 'client',
                            'SampleRate': config['samplerate-zeo']}):
                    return wrapped_call(self, *args, **kw)
            else:
                return wrapped_call(self, *args, **kw)

        instrumented_call.otel_rs_instrumented = True
        MetricImpl.__call__ = instrumented_call

    def _uninstrument(self, **kw):
        for cls, names in {MetricImpl: ['__call__']}:
            for name in names:
                func = getattr(cls, name)
                if not getattr(func, 'otel_rs_instrumented', False):
                    continue
                original = func.__wrapped__
                setattr(cls, name, original)
