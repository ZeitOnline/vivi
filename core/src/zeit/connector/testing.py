from io import BytesIO
import importlib.resources

import transaction
import zope.component

import zeit.cms.testing
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


class ContentFixtureLayer(zeit.cms.testing.ContentFixtureLayer):
    def create_fixture(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        mkdir(connector, ROOT)


SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'], bases=zeit.cms.testing.CONFIG_LAYER
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_ZCML_LAYER)
SQL_CONNECTOR_LAYER = ContentFixtureLayer(SQL_ZOPE_LAYER)


ZOPE_SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql.zope'], bases=zeit.cms.testing.CONFIG_LAYER
)
ZOPE_SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZOPE_SQL_ZCML_LAYER)
ZOPE_SQL_CONNECTOR_LAYER = ContentFixtureLayer(ZOPE_SQL_ZOPE_LAYER)


SQL_CONTENT_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file=str((importlib.resources.files('zeit.cms') / 'ftesting.zcml')),
    features=['zeit.connector.sql.zope'],
    bases=zeit.cms.testing.CONFIG_LAYER,
)
SQL_CONTENT_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_CONTENT_ZCML_LAYER)
SQL_CONTENT_LAYER = ContentFixtureLayer(SQL_CONTENT_ZOPE_LAYER)


COLUMNS_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='testing-columns.zcml', bases=zeit.cms.testing.CONFIG_LAYER
)
COLUMNS_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(COLUMNS_ZCML_LAYER)


class TestCase(zeit.cms.testing.FunctionalTestCase):
    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def get_resource(
        self,
        name,
        body=b'',
        properties=None,
        is_collection=False,
        type='testing',
        uuid=None,
    ):
        if not isinstance(body, bytes):
            body = body.encode('utf-8')
        if uuid is not None:
            if properties is None:
                properties = {}
            properties[('uuid', 'http://namespaces.zeit.de/CMS/document')] = '{urn:uuid:%s}' % uuid
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
