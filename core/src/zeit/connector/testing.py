# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import StringIO
import ZODB.blob
import inspect
import os
import pkg_resources
import re
import urlparse
import zc.queue.tests
import zeit.connector.connector
import zeit.connector.interfaces
import zope.app.testing.functional
import zope.component.hooks
import zope.testing.renormalizing


# XXX copied from zeit.cms; we need zeit.testing!
def ZCMLLayer(
    config_file, module=None, name=None, allow_teardown=True,
    product_config=None):
    if module is None:
        module = inspect.stack()[1][0].f_globals['__name__']
    if name is None:
        name = 'ZCMLLayer(%s)' % config_file
    if not config_file.startswith('/'):
        config_file = pkg_resources.resource_filename(module, config_file)
    def setUp(cls):
        cls.setup = zope.app.testing.functional.FunctionalTestSetup(
            config_file, product_config=product_config)

    def tearDown(cls):
        cls.setup.tearDownCompletely()
        if not allow_teardown:
            raise NotImplementedError

    layer = type(name, (object,), dict(
        __module__=module,
        setUp=classmethod(setUp),
        tearDown=classmethod(tearDown),
    ))
    return layer


zope_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'zope_connector_layer', allow_teardown=True)


real_connector_zcml_layer = ZCMLLayer('ftesting-real.zcml')


class real_connector_layer(real_connector_zcml_layer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        cls.connector = zeit.connector.connector.Connector(roots={
            "default": os.environ['connector-url'],
            "search": os.environ['search-connector-url']})
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(
            cls.connector, zeit.connector.interfaces.IConnector)

    @classmethod
    def testTearDown(cls):
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterUtility(
            cls.connector, zeit.connector.interfaces.IConnector)
        del cls.connector


mock_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting-mock.zcml'),
    __name__, 'mock_connector_layer', allow_teardown=True)


optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
             doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)


class TestCase(zope.app.testing.functional.FunctionalTestCase):

    def get_resource(self, name, body, properties={},
                     contentType='text/plain'):
        rid = 'http://xml.zeit.de/testing/' + name
        return zeit.connector.resource.Resource(
            rid, name, 'testing',
            StringIO.StringIO(body),
            properties=properties,
            contentType=contentType)


class ConnectorTest(TestCase):

    layer = real_connector_layer

    def setUp(self):
        super(ConnectorTest, self).setUp()
        self.connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)

    def tearDown(self):
        reset_testing_folder(self)
        super(ConnectorTest, self).tearDown()


class MockTest(ConnectorTest):

    layer = mock_connector_layer

    def setUp(self):
        super(MockTest, self).setUp()
        self.connector._reset()
        self.connector.add(self.get_resource(
            '', '', contentType='httpd/x-unix-directory'))


parsed_url = urlparse.urlparse(os.environ['connector-url'])
checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(str(parsed_url.hostname)), '<DAVHOST>'),
    (re.compile(str(parsed_url.port)), '<DAVPORT>'),
    ])


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', real_connector_layer)
    kw['package'] = 'zeit.connector'
    kw['checker'] = checker
    kw['optionflags'] = optionflags
    kw['tearDown'] = reset_testing_folder
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test


def reset_testing_folder(test):
    no_site = object()
    old_site = no_site
    if hasattr(test, 'globs'):
        root = test.globs['getRootFolder']()
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(root)

    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    for name, uid in connector.listCollection(
        'http://xml.zeit.de/testing/'):
        del connector[uid]

    if old_site is not no_site:
        zope.component.hooks.setSite(old_site)


def get_storage(blob_dir):
    storage = zc.queue.tests.ConflictResolvingMappingStorage('test')
    blob_storage = ZODB.blob.BlobStorage(blob_dir, storage)
    return blob_storage


def print_tree(connector, base):
    """Helper to print a tree."""
    print '\n'.join(list_tree(connector, base))


def list_tree(connector, base, level=0):
    """Helper to print a tree."""
    result = []
    if level == 0:
        result.append(base)
    for name, uid in sorted(connector.listCollection(base)):
        result.append('%s %s' % (uid, connector[uid].type))
        if uid.endswith('/'):
            result.extend(list_tree(connector, uid, level+1))

    return result
