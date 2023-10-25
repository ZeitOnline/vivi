from relstorage.zodburi_resolver import RelStorageURIResolver, Resolver
import ZODB.serialize
import zeit.cms.cli
import zodburi


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
