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


def run_migrations_offline(params) -> None:
    context.configure(
        url='postgresql://unused',
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        transaction_per_migration=True,
        **params,
    )
    context.run_migrations()


def run_migrations_online(params) -> None:
    if getattr(context.config.cmd_opts, 'autogenerate', False):
        from zeit.connector.postgresql import METADATA
    else:
        METADATA = None

    args = context.get_x_argument(as_dictionary=True)
    pgservice = args.get('service')
    if not pgservice:
        query = dict(parse_qsl(urlparse(os.environ['vivi_zeit.connector_dsn']).query))
        pgservice = query['service']

    pgopt = ''
    prefix = 'psql.'
    config = context.config.get_section(context.config.config_ini_section)
    for key, value in config.items():
        if not key.startswith(prefix):
            continue
        key = key.replace(prefix, '', 1)
        pgopt += f'-c%20{key}={value}%20'
    dsn = f'postgresql:///?service={pgservice}&options={pgopt}'

    engine = create_engine(dsn, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=METADATA,
            transaction_per_migration=True,
            **params,
        )
        context.run_migrations()


params = {'version_table': context.config.get_main_option('version_table')}
if context.is_offline_mode():
    run_migrations_offline(params)
else:
    run_migrations_online(params)
