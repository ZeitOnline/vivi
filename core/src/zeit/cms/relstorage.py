import functools
import logging

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from perfmetrics.metric import _AbstractMetricImpl as MetricImpl
from relstorage.zodburi_resolver import RelStorageURIResolver, Resolver
import opentelemetry.trace
import perfmetrics._util
import ZODB.serialize
import zodburi

import zeit.cms.cli


log = logging.getLogger(__name__)


class PsqlServiceResolver(Resolver):
    def __call__(self, parsed_uri, kw):
        def factory(options):
            from relstorage.adapters.postgresql import PostgreSQLAdapter

            return PostgreSQLAdapter(dsn='service=' + parsed_uri.hostname, options=options)

        return factory, kw


psql_resolver = RelStorageURIResolver(PsqlServiceResolver())


class SocketResolver(Resolver):
    def __call__(self, parsed_uri, kw):
        def factory(options):
            from relstorage.adapters.postgresql import PostgreSQLAdapter

            args = {
                'host': parsed_uri.path,
                'user': parsed_uri.username,
                'password': parsed_uri.password,
                'dbname': parsed_uri.hostname,
            }

            return PostgreSQLAdapter(
                dsn=' '.join(f"{k}='{v}'" for k, v in args.items()), options=options
            )

        return factory, kw


socket_resolver = RelStorageURIResolver(SocketResolver())


def zodbpack():
    import psycopg2  # soft dependency

    settings = zeit.cms.cli.parse_paste_ini()
    storage_factory, db_kw = zodburi.resolve_uri(settings['zodbconn.uri'])
    storage = storage_factory()

    # Work around zodb/relstorage#482
    conn = psycopg2.connect(storage._adapter._dsn)
    cur = conn.cursor()
    log.info('Workaround: truncating object_refs_added table')
    cur.execute('TRUNCATE object_refs_added')
    conn.commit()
    conn.close()

    # We use keep_history=False, so we run pack only for garbage collection
    timestamp = None
    storage.pack(timestamp, ZODB.serialize.referencesf)
    storage.close()


class RelStorageInstrumentor(BaseInstrumentor):
    """The relstorage codebase is already instrumented for statsd via the
    `perfmetrics` library, so we hook into that to trace relevant functions.
    """

    def instrumentation_dependencies(self):
        return ('relstorage >= 3.5',)

    def _instrument(self, **kw):
        tracer = opentelemetry.trace.get_tracer(__name__, tracer_provider=kw.get('tracer_provider'))

        if not perfmetrics._util.PURE_PYTHON:
            log.warning('perfmetrics loaded C extensions, skipping instrumentation')
            return

        wrapped_call = MetricImpl.__call__

        @functools.wraps(wrapped_call)
        def instrumented_call(self, *args, **kw):
            samplerate = opentelemetry.context.get_value(__name__)
            if samplerate:
                operation = self.stat_name or self._compute_stat(args)
                with tracer.start_as_current_span(
                    operation,
                    attributes={'span.kind': 'client', 'SampleRate': samplerate},
                ):
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
