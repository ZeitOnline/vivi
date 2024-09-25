from io import BytesIO
import contextlib
import importlib.resources
import inspect
import os
import socket
import time

from gcp_storage_emulator.server import create_server as create_gcp_server
from sqlalchemy import text as sql
from sqlalchemy.exc import OperationalError
import docker
import plone.testing
import requests
import sqlalchemy
import transaction
import zope.component.hooks
import zope.testing.renormalizing

import zeit.cms.testing
import zeit.connector.gcsemulator  # activate monkey patches
import zeit.connector.interfaces
import zeit.connector.mock
import zeit.connector.models


ROOT = 'http://xml.zeit.de/testing'


class DockerSetupError(requests.exceptions.ConnectionError):
    # for more informative error output
    pass


# Taken from pytest-nginx
def get_random_port():
    s = socket.socket()
    with contextlib.closing(s):
        s.bind(('localhost', 0))
        return s.getsockname()[1]


FILESYSTEM_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.filesystem'], bases=(zeit.cms.testing.CONFIG_LAYER,)
)
FILESYSTEM_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(bases=(FILESYSTEM_ZCML_LAYER,))

MOCK_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.mock'], bases=(zeit.cms.testing.CONFIG_LAYER,)
)
MOCK_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(bases=(MOCK_ZCML_LAYER,))


class SQLServerLayer(plone.testing.Layer):
    container_image = 'postgres:14'

    def setUp(self):
        self['docker'] = docker.from_env()
        port = get_random_port()
        try:
            self['psql_container'] = self['docker'].containers.run(
                self.container_image,
                detach=True,
                remove=True,
                environment={'POSTGRES_PASSWORD': 'postgres'},
                ports={5432: port},
            )
        except requests.exceptions.ConnectionError:
            raise DockerSetupError("Couldn't start docker container, is docker running?")

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
        self['docker'].close()
        del self['docker']


SQL_SERVER_LAYER = SQLServerLayer()


class GCSServerLayer(plone.testing.Layer):
    bucket = 'vivi-test'

    def setUp(self):
        self['gcp_server'] = create_gcp_server(
            'localhost', 0, in_memory=True, default_bucket=self.bucket
        )
        self['gcp_server'].start()
        _, port = self['gcp_server']._api._httpd.socket.getsockname()
        # Evaluated automatically by google.cloud.storage.Client
        os.environ['STORAGE_EMULATOR_HOST'] = 'http://localhost:%s' % port

    def tearDown(self):
        self['gcp_server'].stop()
        del self['gcp_server']


GCS_SERVER_LAYER = GCSServerLayer()


class SQLConfigLayer(zeit.cms.testing.ProductConfigLayer):
    defaultBases = (
        SQL_SERVER_LAYER,
        GCS_SERVER_LAYER,
    )

    def __init__(self):
        super().__init__(
            {
                'storage-project': 'ignored_by_emulator',
                'storage-bucket': GCS_SERVER_LAYER.bucket,
                'sql-locking': 'True',
            }
        )

    def setUp(self):
        self.config['dsn'] = self['dsn']
        os.environ.setdefault('PGDATABASE', 'vivi_test')
        super().setUp()


SQL_CONFIG_LAYER = SQLConfigLayer()


class SQLDatabaseLayer(plone.testing.Layer):
    def __init__(self, name='SQLDatabaseLayer', module=None, bases=()):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        super().__init__(name=name, module=module, bases=bases)

    def setUp(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        engine = connector.engine
        try:
            self['sql_connection'] = engine.connect()
        except OperationalError:  # Create database
            db = os.environ['PGDATABASE']
            os.environ['PGDATABASE'] = 'template1'
            c = engine.connect()
            c.connection.driver_connection.set_isolation_level(0)
            c.execute(sql('CREATE DATABASE %s' % db))
            c.connection.driver_connection.set_isolation_level(1)
            c.close()
            os.environ['PGDATABASE'] = db
            self['sql_connection'] = engine.connect()

        # Make sqlalchemy use only this specific connection, so we can apply a
        # nested transaction in testSetUp()
        connector.session.configure(bind=self['sql_connection'])

        # Create tables
        c = self['sql_connection']
        t = c.begin()
        zeit.connector.models.Base.metadata.drop_all(c)
        zeit.connector.models.Base.metadata.create_all(c)
        t.commit()

    def tearDown(self):
        self['sql_connection'].close()
        del self['sql_connection']

    def testSetUp(self):
        """Sets up a transaction savepoint, which will be rolled back
        after each test. See <https://docs.sqlalchemy.org/en/14/orm/
         session_transaction.html#joining-a-session-into-an-external-transaction
         -such-as-for-test-suites>
        Note that the example operates with a single session object, whereas we
        tie the connection to the session factory instead.
        """
        connection = self['sql_connection']
        # Begin a non-orm transaction which we roll back in testTearDown().
        self['sql_transaction'] = connection.begin()

        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        # Begin savepoint, so we can use transaction.abort() during tests.
        self['sql_nested'] = connection.begin_nested()
        self['sql_session'] = connector.session()
        sqlalchemy.event.listen(self['sql_session'], 'after_transaction_end', self.end_savepoint)

        with zeit.cms.testing.site(self['zodbApp']):
            mkdir(connector, ROOT)
        transaction.commit()

    def end_savepoint(self, session, transaction):
        if not self['sql_nested'].is_active:
            self['sql_nested'] = self['sql_connection'].begin_nested()

    def testTearDown(self):
        transaction.abort()

        sqlalchemy.event.remove(self['sql_session'], 'after_transaction_end', self.end_savepoint)
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        connector.session.remove()
        del self['sql_session']

        self['sql_transaction'].rollback()
        del self['sql_transaction']
        del self['sql_nested']


SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'], bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER)
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_ZCML_LAYER,))
SQL_CONNECTOR_LAYER = SQLDatabaseLayer(bases=(SQL_ZOPE_LAYER,))


ZOPE_SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql.zope'], bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER)
)
ZOPE_SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZOPE_SQL_ZCML_LAYER,))
ZOPE_SQL_CONNECTOR_LAYER = SQLDatabaseLayer(bases=(ZOPE_SQL_ZOPE_LAYER,))


SQL_CONTENT_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    str((importlib.resources.files('zeit.cms') / 'ftesting.zcml')),
    features=['zeit.connector.sql.zope'],
    bases=(zeit.cms.testing.CONFIG_LAYER, SQL_CONFIG_LAYER),
)
SQL_CONTENT_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_CONTENT_ZCML_LAYER,))
SQL_CONTENT_LAYER = SQLDatabaseLayer(bases=(SQL_CONTENT_ZOPE_LAYER,))


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
