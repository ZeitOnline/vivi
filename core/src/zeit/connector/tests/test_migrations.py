from difflib import unified_diff
import importlib.resources
import unittest

from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import text as sql
from sqlalchemy.pool import NullPool
import alembic.config
import alembic.script
import sqlalchemy

import zeit.connector.testing


class MigrationsTest(unittest.TestCase):
    layer = zeit.connector.testing.SQL_SERVER_LAYER
    dbname = 'vivi_migrations'

    def setUp(self):
        self.admin = sqlalchemy.create_engine(self.layer['dsn'] + '/template1', poolclass=NullPool)
        self.engine = sqlalchemy.create_engine(
            self.layer['dsn'] + '/' + self.dbname, poolclass=NullPool
        )

    def tearDown(self):
        self.engine.dispose()
        self.admin.dispose()

    def createdb(self):
        c = self.admin.connect()
        c.connection.driver_connection.set_isolation_level(0)
        c.execute(sql(f'CREATE DATABASE {self.dbname}'))
        c.close()

    def dropdb(self):
        c = self.admin.connect()
        c.connection.driver_connection.set_isolation_level(0)
        c.execute(sql(f'DROP DATABASE {self.dbname}'))
        c.close()

    def dump_schema(self, connection):
        metadata = sqlalchemy.MetaData()
        metadata.reflect(connection)

        result = []
        engine = sqlalchemy.create_mock_engine(
            'postgresql://',
            lambda query, *args, **kw: result.append(str(query.compile(dialect=engine.dialect))),
        )
        metadata.create_all(engine, checkfirst=False)
        return result[0].splitlines()

    def alembic_upgrade(self, connection, name, target='head'):
        config = alembic.config.Config(
            importlib.resources.files(zeit.connector) / 'migrations/alembic.ini',
            ini_section=name,
        )
        script = alembic.script.ScriptDirectory.from_config(config)
        with EnvironmentContext(config=config, script=script) as context:
            context.configure(
                connection=connection,
                destination_rev=target,
                fn=lambda rev, context: script._upgrade_revs(target, rev),
                transaction_per_migration=True,
            )
            context.run_migrations()
        connection.execute(sql('DROP TABLE alembic_version'))
        connection.commit()

    def test_migrations_create_same_schema_as_from_scratch(self):
        self.createdb()
        c = self.engine.connect()
        zeit.connector.postgresql.METADATA.create_all(c)
        scratch = self.dump_schema(c)
        c.close()
        self.dropdb()

        self.createdb()
        c = self.engine.connect()
        self.alembic_upgrade(c, 'predeploy')
        c.close()
        c = self.engine.connect()
        self.alembic_upgrade(c, 'postdeploy')
        migrations = self.dump_schema(c)
        c.close()
        self.dropdb()

        diff = unified_diff(scratch, migrations, n=5)
        self.assertEqual(scratch, migrations, '\n'.join(diff))
