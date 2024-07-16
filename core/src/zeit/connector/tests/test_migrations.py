from difflib import unified_diff
from subprocess import PIPE
import importlib.resources
import io
import os
import re
import subprocess
import unittest

from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import text as sql
from sqlalchemy.pool import NullPool
import alembic.config
import alembic.script
import sqlalchemy

import zeit.connector.testing


class DBTestCase(unittest.TestCase):
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
        def _dump(sql, *args, **kw):
            text = str(sql.compile(dialect=engine.dialect))
            text = re.sub(r'\n+', '\n', text)
            result.append(text)

        metadata = sqlalchemy.MetaData()
        metadata.reflect(connection)

        result = []
        engine = sqlalchemy.create_mock_engine(
            'postgresql://',
            executor=_dump,
        )
        metadata.create_all(engine, checkfirst=False)
        return sorted(result)


def alembic_upgrade(connection, name, **kw):
    if connection is None:
        kw['url'] = 'postgresql://unused'
        kw['literal_binds'] = True
        kw['dialect_ops'] = {'paramstyle': 'named'}

    config = alembic.config.Config(
        importlib.resources.files(zeit.connector) / 'migrations/alembic.ini',
        ini_section=name,
    )
    script = alembic.script.ScriptDirectory.from_config(config)
    with EnvironmentContext(config=config, script=script, as_sql=connection is None) as context:
        context.configure(
            connection=connection,
            fn=lambda rev, context: script._upgrade_revs('head', rev),
            transaction_per_migration=True,
            **kw,
        )
        context.run_migrations()

    if connection is not None:
        connection.execute(sql('DROP TABLE alembic_version'))
        connection.commit()


class MigrationsTest(DBTestCase):
    def test_migrations_create_same_schema_as_from_scratch(self):
        self.createdb()
        c = self.engine.connect()
        zeit.connector.postgresql.METADATA.create_all(c)
        scratch = self.dump_schema(c)
        c.close()
        self.dropdb()

        self.createdb()
        c = self.engine.connect()
        alembic_upgrade(c, 'predeploy')
        c.close()
        c = self.engine.connect()
        alembic_upgrade(c, 'postdeploy')
        migrations = self.dump_schema(c)
        c.close()
        self.dropdb()

        diff = unified_diff(scratch, migrations, n=5)
        self.assertEqual(scratch, migrations, '\n'.join(diff))


class MigrationsLint(unittest.TestCase):
    def test_lint_migrations_with_squawk(self):
        buffer = io.StringIO()
        for name in ['predeploy', 'postdeploy']:
            alembic_upgrade(None, name, output_buffer=buffer)
        sql = [x.strip() for x in buffer.getvalue().split(';')]
        # squawk ignores any statements that refer to a newly created table
        sql = [x for x in sql if not x.startswith('CREATE TABLE')]
        sql = ';\n'.join(sql)

        squawk = os.environ['SQUAWK_COMMAND']
        proc = subprocess.Popen([squawk], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = proc.communicate(sql.encode('utf-8'))
        if proc.returncode:
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            self.fail('squawk returned errors:\n' + output)
