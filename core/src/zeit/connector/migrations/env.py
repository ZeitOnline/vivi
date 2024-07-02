from urllib.parse import parse_qsl, urlparse
import logging
import os

from alembic import context
from sqlalchemy import create_engine, pool

import zeit.cms.cli


if 'logging.root.level' in os.environ:
    zeit.cms.cli._configure_logging(os.environ)
else:
    logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)-5.5s %(name)s %(message)s')


def run_migrations_offline() -> None:
    context.configure(
        url='postgresql://unused',
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        transaction_per_migration=True,
        **params,
    )
    context.run_migrations()


def run_migrations_online() -> None:
    if getattr(context.config.cmd_opts, 'autogenerate', False):
        from zeit.connector.postgresql import METADATA
    else:
        METADATA = None

    args = context.get_x_argument(as_dictionary=True)
    pgservice = args.get('service')
    if pgservice:
        dsn = f'postgresql://?service={pgservice}'
    else:
        query = dict(parse_qsl(urlparse(os.environ['vivi_zeit.connector_dsn']).query))
        pgservice = query['service']
    dsn = f'postgresql:///?service={pgservice}'

    engine = create_engine(dsn, poolclass=pool.NullPool)
    with engine.connect() as connection:
        logging.getLogger('alembic.runtime.migration').info('Connecting to %s', dsn)
        context.configure(
            connection=connection,
            target_metadata=METADATA,
            transaction_per_migration=True,
            **params,
        )
        context.run_migrations()


params = {'version_table': context.config.get_main_option('version_table')}

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
