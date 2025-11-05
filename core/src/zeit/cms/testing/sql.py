import os
import time

from sqlalchemy import text as sql
from sqlalchemy.exc import OperationalError
import gcp_storage_emulator.server
import sqlalchemy

import zeit.connector.interfaces
import zeit.connector.models
import zeit.connector.postgresql

from . import gcsemulator  # noqa activate monkey patches
from .docker import LAYER as DOCKER_LAYER
from .docker import get_random_port
from .layer import Layer
from .zope import ProductConfigLayer


class SQLServerLayer(Layer):
    defaultBases = (DOCKER_LAYER,)

    container_image = 'postgres:14'

    def setUp(self):
        port = get_random_port()
        self['psql_container'] = DOCKER_LAYER.run_container(
            self.container_image,
            detach=True,
            remove=True,
            environment={'POSTGRES_PASSWORD': 'postgres'},
            ports={5432: port},
        )
        self['dsn'] = f'postgresql://postgres:postgres@localhost:{port}'
        self.wait_for_startup(self['dsn'])

    def wait_for_startup(self, dsn, timeout=10, sleep=0.2):
        engine = sqlalchemy.create_engine(dsn)
        slept = 0
        while slept < timeout:
            slept += sleep
            time.sleep(sleep)
            try:
                engine.connect()
            except Exception:
                pass
            else:
                engine.dispose()
                return
        print(self['psql_container'].logs(timestamps=True).decode('utf-8'))
        raise RuntimeError('%s did not start up' % dsn)

    def tearDown(self):
        del self['dsn']
        self['psql_container'].stop()
        del self['psql_container']


SQL_SERVER_LAYER = SQLServerLayer()


class DatabaseLayer(Layer):
    defaultBases = (SQL_SERVER_LAYER,)
    dbname = 'vivi_test'

    def setUp(self):
        dsn = self['dsn']
        self['dsn'] += f'/{self.dbname}'

        engine = sqlalchemy.create_engine(self['dsn'])
        try:
            engine.connect()
            return
        except OperationalError:
            pass  # Database does not exist yet, have to create it

        engine = sqlalchemy.create_engine(f'{dsn}/template1')
        with engine.connect() as c:
            c.connection.driver_connection.set_isolation_level(0)
            c.execute(sql(f'CREATE DATABASE {self.dbname}'))
        engine.dispose()

        engine = sqlalchemy.create_engine(self['dsn'])
        self['sql_engine'] = engine
        self['sql_connection'] = c = engine.connect()
        t = self['sql_connection'].begin()
        zeit.connector.models.Base.metadata.drop_all(c)
        zeit.connector.models.Base.metadata.create_all(c)
        t.commit()

    def tearDown(self):
        self['sql_connection'].close()
        del self['sql_connection']
        self['sql_engine'].dispose()
        del self['sql_engine']
        del self['dsn']

    def testSetUp(self):
        c = self['sql_connection']
        t = c.begin()
        for mapper in zeit.connector.models.Base.registry.mappers:
            table = mapper.class_.__tablename__
            c.execute(sql(f'truncate {table} cascade'))
        t.commit()


DATABASE_LAYER = DatabaseLayer()


class GCSServerLayer(Layer):
    bucket = 'vivi-test'

    def setUp(self):
        self['gcs_storage'] = gcsemulator.StackableMemoryStorage()
        gcp_storage_emulator.handlers.buckets.create_bucket(self.bucket, self['gcs_storage'])
        self['gcs_server'] = gcp_storage_emulator.server.APIThread(
            'localhost', 0, self['gcs_storage']
        )
        self['gcs_server'].start()
        self['gcs_server'].is_running.wait()
        _, port = self['gcs_server']._httpd.socket.getsockname()
        # Evaluated automatically by google.cloud.storage.Client
        os.environ['STORAGE_EMULATOR_HOST'] = 'http://localhost:%s' % port

    def testSetUp(self):
        self['gcs_storage'].stack_push()

    def testTearDown(self):
        self['gcs_storage'].stack_pop()

    def tearDown(self):
        self['gcs_server'].join(timeout=1)
        del self['gcs_server']


GCS_SERVER_LAYER = GCSServerLayer()


class SQLConfigLayer(ProductConfigLayer):
    defaultBases = (
        DATABASE_LAYER,
        GCS_SERVER_LAYER,
    )

    def __init__(self, *args, **kw):
        super().__init__(
            {
                'storage-project': 'ignored_by_emulator',
                'storage-bucket': GCS_SERVER_LAYER.bucket,
                'sql-locking': 'True',
                'sql-pool-class': 'sqlalchemy.pool.NullPool',
            },
            *args,
            **kw,
        )

    def setUp(self):
        self.config['dsn'] = self['dsn']
        super().setUp()


SQL_CONFIG_LAYER = SQLConfigLayer(package='zeit.connector')
