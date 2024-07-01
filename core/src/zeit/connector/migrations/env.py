import logging
import os

from alembic import context
from sqlalchemy import create_engine, pool


# Use env-var based zeit.cms.logging instead?
logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)-5.5s %(name)s %(message)s')

target_metadata = None


def run_migrations_offline() -> None:
    context.configure(
        url='postgresql://unused',
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    args = context.get_x_argument(as_dictionary=True)
    pgservice = args.get('service')
    if pgservice:
        dsn = f'postgresql://?service={pgservice}'
    else:
        dsn = os.environ['vivi_zeit.connector_dsn']

    engine = create_engine(dsn, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
