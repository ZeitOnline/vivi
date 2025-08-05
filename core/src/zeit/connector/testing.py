from io import BytesIO
import importlib.resources
import os
import time

from gcp_storage_emulator.server import create_server as create_gcp_server
from sqlalchemy import text as sql
from sqlalchemy.exc import OperationalError
import requests
import sqlalchemy
import transaction
import zope.component.hooks

import zeit.cms.testing
import zeit.connector.gcsemulator  # activate monkey patches
import zeit.connector.interfaces
import zeit.connector.mock
import zeit.connector.models


ROOT = 'http://xml.zeit.de/testing'


FILESYSTEM_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.filesystem'], bases=zeit.cms.testing.CONFIG_LAYER
)
FILESYSTEM_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(FILESYSTEM_ZCML_LAYER)

MOCK_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.mock'], bases=zeit.cms.testing.CONFIG_LAYER
)
MOCK_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(MOCK_ZCML_LAYER)


class SQLServerLayer(zeit.cms.testing.Layer):
    defaultBases = (zeit.cms.testing.DOCKER_LAYER,)

    container_image = 'postgres:14'

    def setUp(self):
        port = zeit.cms.testing.get_random_port()
        self['psql_container'] = zeit.cms.testing.DOCKER_LAYER.run_container(
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


class GCSServerLayer(zeit.cms.testing.Layer):
    bucket = 'vivi-test'

    def setUp(self):
        self['gcp_server'] = create_gcp_server(
            'localhost', 0, in_memory=True, default_bucket=self.bucket
        )
        self['gcp_server'].start()
        _, port = self['gcp_server']._api._httpd.socket.getsockname()
        # Evaluated automatically by google.cloud.storage.Client
        os.environ['STORAGE_EMULATOR_HOST'] = 'http://localhost:%s' % port

    def testSetUp(self):
        requests.get(os.environ['STORAGE_EMULATOR_HOST'] + '/wipe?keep-buckets=True')

    def tearDown(self):
        self['gcp_server'].stop()
        del self['gcp_server']


GCS_SERVER_LAYER = GCSServerLayer()


class SQLDatabaseLayer(zeit.cms.testing.Layer):
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
        with engine.connect() as c:
            t = c.begin()
            zeit.connector.models.Base.metadata.drop_all(c)
            zeit.connector.models.Base.metadata.create_all(c)
            t.commit()
        engine.dispose()

    def tearDown(self):
        del self['dsn']


SQL_DATABASE_LAYER = SQLDatabaseLayer()


class SQLConfigLayer(zeit.cms.testing.ProductConfigLayer):
    defaultBases = (
        SQL_DATABASE_LAYER,
        GCS_SERVER_LAYER,
    )

    def __init__(self):
        super().__init__(
            {
                'storage-project': 'ignored_by_emulator',
                'storage-bucket': GCS_SERVER_LAYER.bucket,
                'sql-locking': 'True',
                'sql-pool-class': 'sqlalchemy.pool.NullPool',
            }
        )

    def setUp(self):
        self.config['dsn'] = self['dsn']
        super().setUp()


SQL_CONFIG_LAYER = SQLConfigLayer()


class SQLIsolationLayer(zeit.cms.testing.Layer):
    def setUp(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        self['sql_connection'] = connector.engine.connect()

        # Configure sqlalchemy session to use only this specific connection,
        # and to use savepoints instead of full commits. Thus it joins the
        # transaction that we start in testSetUp() and roll back in testTearDown()
        # See "Joining a Session into an External Transaction" in the sqlalchemy doc
        connector.session.configure(
            bind=self['sql_connection'], join_transaction_mode='create_savepoint'
        )

        self['sql_transaction_layer'] = self['sql_connection'].begin()

    def tearDown(self):
        self['sql_transaction_layer'].rollback()
        del self['sql_transaction_layer']
        self['sql_connection'].close()
        del self['sql_connection']

    def testSetUp(self):
        self['sql_transaction_test'] = self['sql_connection'].begin_nested()

    def testTearDown(self):
        transaction.abort()  # includes connector.session.close()
        self['sql_transaction_test'].rollback()
        del self['sql_transaction_test']


class ContentFixtureLayer(zeit.cms.testing.Layer):
    def setUp(self):
        self['sql_transaction_test'] = self['sql_connection'].begin_nested()
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        zcml = zope.app.appsetup.appsetup.getConfigContext()
        if zcml.hasFeature('zeit.connector.sql.zope'):
            with self['rootFolder'](self['zodbDB-layer']) as root:
                with zeit.cms.testing.site(root):
                    mkdir(connector, ROOT)
        else:
            mkdir(connector, ROOT)
        transaction.commit()

    def tearDown(self):
        self['sql_transaction_test'].rollback()
        del self['sql_transaction_test']


SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'], bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER)
)
SQL_SQL_LAYER = SQLIsolationLayer(SQL_ZCML_LAYER)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_SQL_LAYER)
SQL_CONNECTOR_LAYER = ContentFixtureLayer(SQL_ZOPE_LAYER)


ZOPE_SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql.zope'], bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER)
)
ZOPE_SQL_SQL_LAYER = SQLIsolationLayer(ZOPE_SQL_ZCML_LAYER)
ZOPE_SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZOPE_SQL_SQL_LAYER)
ZOPE_SQL_CONNECTOR_LAYER = ContentFixtureLayer(ZOPE_SQL_ZOPE_LAYER)


SQL_CONTENT_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file=str((importlib.resources.files('zeit.cms') / 'ftesting.zcml')),
    features=['zeit.connector.sql.zope'],
    bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER),
)
SQL_CONTENT_SQL_LAYER = SQLIsolationLayer(SQL_CONTENT_ZCML_LAYER)
SQL_CONTENT_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_CONTENT_SQL_LAYER)
SQL_CONTENT_LAYER = ContentFixtureLayer(SQL_CONTENT_ZOPE_LAYER)


COLUMNS_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='testing-columns.zcml', bases=zeit.cms.testing.CONFIG_LAYER
)
COLUMNS_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(COLUMNS_ZCML_LAYER)


class TestCase(zeit.cms.testing.FunctionalTestCase):
    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def get_resource(self, name, body=b'', properties=None, is_collection=False, type='testing'):
        if not isinstance(body, bytes):
            body = body.encode('utf-8')
        return zeit.connector.resource.Resource(
            f'{ROOT}/{name}',
            name,
            type,
            BytesIO(body),
            properties=properties,
            is_collection=is_collection,
        )

    def add_resource(self, name, **kw):
        r = self.get_resource(name, **kw)
        self.connector[r.id] = r
        r = self.connector[r.id]
        transaction.commit()
        return r

    def mkdir(self, name):
        if not name.startswith(ROOT):
            name = f'{ROOT}/{name}'
        return mkdir(self.connector, name)


class FilesystemConnectorTest(TestCase):
    layer = FILESYSTEM_CONNECTOR_LAYER


class MockTest(TestCase):
    layer = MOCK_CONNECTOR_LAYER


class SQLTest(TestCase):
    layer = SQL_CONNECTOR_LAYER


class ZopeSQLTest(TestCase):
    layer = ZOPE_SQL_CONNECTOR_LAYER


def FunctionalDocFileSuite(*paths, **kw):
    kw['package'] = 'zeit.connector'
    return zeit.cms.testing.FunctionalDocFileSuite(*paths, **kw)


def print_tree(connector, base):
    """Helper to print a tree."""
    print('\n'.join(list_tree(connector, base)))


def list_tree(connector, base, level=0):
    """Helper to print a tree."""
    result = []
    if level == 0:
        result.append(base)
    for _name, uid in sorted(connector.listCollection(base)):
        result.append('%s %s' % (uid, connector[uid].type))
        if uid.endswith('/'):
            result.extend(list_tree(connector, uid, level + 1))

    return result


def mkdir(connector, id):
    # Use a made-up type `folder` to differentiate from "no meta:type", which
    # would fall back to `collection`. (Even though the latter value is what we
    # use "in reality" in zeit.cms.repository.folder.)
    res = zeit.connector.resource.Resource(id, None, 'folder', BytesIO(b''), is_collection=True)
    connector.add(res)
    transaction.commit()
    return res


def create_folder_structure(connector):
    """Create a folder structure for copy/move"""

    def add_folder(id):
        mkdir(connector, f'{ROOT}/{id}')

    def add_file(id):
        res = zeit.connector.resource.Resource(f'{ROOT}/{id}', None, 'text', BytesIO(b'Pop.'))
        connector.add(res)

    add_folder('testroot')
    add_folder('testroot/a')
    add_folder('testroot/a/a')
    add_folder('testroot/a/b')
    add_folder('testroot/a/b/c')
    add_folder('testroot/b')
    add_folder('testroot/b/a')
    add_folder('testroot/b/b')

    add_file('testroot/f')
    add_file('testroot/g')
    add_file('testroot/h')
    add_file('testroot/a/f')
    add_file('testroot/a/b/c/foo')
    add_file('testroot/b/b/foo')

    expected_structure = [
        'http://xml.zeit.de/testing/testroot',
        'http://xml.zeit.de/testing/testroot/a/ folder',
        'http://xml.zeit.de/testing/testroot/a/a/ folder',
        'http://xml.zeit.de/testing/testroot/a/b/ folder',
        'http://xml.zeit.de/testing/testroot/a/b/c/ folder',
        'http://xml.zeit.de/testing/testroot/a/b/c/foo text',
        'http://xml.zeit.de/testing/testroot/a/f text',
        'http://xml.zeit.de/testing/testroot/b/ folder',
        'http://xml.zeit.de/testing/testroot/b/a/ folder',
        'http://xml.zeit.de/testing/testroot/b/b/ folder',
        'http://xml.zeit.de/testing/testroot/b/b/foo text',
        'http://xml.zeit.de/testing/testroot/f text',
        'http://xml.zeit.de/testing/testroot/g text',
        'http://xml.zeit.de/testing/testroot/h text',
    ]
    assert expected_structure == list_tree(connector, 'http://xml.zeit.de/testing/testroot')


def copy_inherited_functions(base, locals):
    """py.test annotates the test function object with data, e.g. required
    fixtures. Normal inheritance means that there is only *one* function object
    (in the base class), which means for example that subclasses cannot specify
    different layers, since they would all aggregate on that one function
    object, which would be completely wrong.

    """

    def make_delegate(name):
        def delegate(self):
            return getattr(super(type(self), self), name)()

        return delegate

    for name in dir(base):
        if not name.startswith('test_'):
            continue
        if name in locals:
            raise KeyError(f'{name} already exists')
        locals[name] = make_delegate(name)
