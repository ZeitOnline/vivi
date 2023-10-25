from relstorage.zodburi_resolver import RelStorageURIResolver, Resolver


class PsqlServiceResolver(Resolver):

    def __call__(self, parsed_uri, kw):
        def factory(options):
            from relstorage.adapters.postgresql import PostgreSQLAdapter
            return PostgreSQLAdapter(
                dsn='service=' + parsed_uri.hostname, options=options)
        return factory, kw


psql_resolver = RelStorageURIResolver(PsqlServiceResolver())
