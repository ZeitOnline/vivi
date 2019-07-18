import StringIO
import ZODB.blob
import doctest
import inspect
import os
import pkg_resources
import re
import time
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
        testfolder='testing'
    ))
    return layer


zope_connector_layer = ZCMLLayer('ftesting.zcml')


real_connector_zcml_layer = ZCMLLayer('ftesting-real.zcml')


class real_connector_layer(real_connector_zcml_layer):

    @classmethod
    def setUp(cls):
        cls.testfolder = 'testing/%s' % time.time()
        mkdir(cls._create_connector(),
              'http://xml.zeit.de/%s' % cls.testfolder)

    @classmethod
    def tearDown(cls):
        del cls._create_connector()['http://xml.zeit.de/%s' % cls.testfolder]

    @classmethod
    def _create_connector(cls):
        return zeit.connector.connector.Connector(roots={
            "default": os.environ['connector-url'],
            "search": os.environ['search-connector-url']})

    @classmethod
    def testSetUp(cls):
        cls.connector = cls._create_connector()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(
            cls.connector, zeit.connector.interfaces.IConnector)

    @classmethod
    def testTearDown(cls):
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterUtility(
            cls.connector, zeit.connector.interfaces.IConnector)
        del cls.connector


filesystem_connector_layer = ZCMLLayer(
    'ftesting-filesystem.zcml',
    product_config="""\
<product-config zeit.connector>
repository-path %s
</product-config>
""" % pkg_resources.resource_filename('zeit.connector', 'testcontent'))


mock_connector_layer = ZCMLLayer('ftesting-mock.zcml')


optionflags = (
    doctest.REPORT_NDIFF +
    doctest.NORMALIZE_WHITESPACE +
    doctest.ELLIPSIS)


class TestCase(zope.app.testing.functional.FunctionalTestCase):

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_resource(self, name, body, properties={},
                     contentType='text/plain'):
        rid = 'http://xml.zeit.de/%s/%s' % (self.layer.testfolder, name)
        return zeit.connector.resource.Resource(
            rid, name, 'testing',
            StringIO.StringIO(body),
            properties=properties,
            contentType=contentType)


class ConnectorTest(TestCase):

    layer = real_connector_layer
    level = 2

    def tearDown(self):
        reset_testing_folder(self)
        super(ConnectorTest, self).tearDown()


class FilesystemConnectorTest(TestCase):

    layer = filesystem_connector_layer


class MockTest(TestCase):

    layer = mock_connector_layer

    def setUp(self):
        super(MockTest, self).setUp()
        self.connector._reset()
        # I don't really get what this is here for, but removing it breaks
        # tests:
        self.connector.add(self.get_resource(
            '', '', contentType='httpd/x-unix-directory'))


# XXX copy&paste from zeit.cms.testing
class OutputChecker(zope.testing.renormalizing.RENormalizing):

    def check_output(self, want, got, optionflags):
        # `want` is already unicode, since we pass `encoding` to DocFileSuite.
        if isinstance(got, str):
            got = got.decode('utf-8')
        super_ = zope.testing.renormalizing.RENormalizing
        return super_.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        if isinstance(got, str):
            got = got.decode('utf-8')
        super_ = zope.testing.renormalizing.RENormalizing
        return super_.output_difference(self, example, got, optionflags)


parsed_url = urlparse.urlparse(os.environ['connector-url'])
checker = OutputChecker([
    (re.compile(str(parsed_url.hostname)), '<DAVHOST>'),
    (re.compile(str(parsed_url.port)), '<DAVPORT>'),
])


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', real_connector_layer)
    kw['package'] = 'zeit.connector'
    kw['checker'] = checker
    kw['optionflags'] = optionflags
    kw['tearDown'] = reset_testing_folder
    kw['globs'] = {'TESTFOLDER': lambda: layer.testfolder}
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
        testfolder = test.globs['TESTFOLDER']()
    else:
        testfolder = test.layer.testfolder

    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    for name, uid in connector.listCollection(
            'http://xml.zeit.de/' + testfolder):
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
            result.extend(list_tree(connector, uid, level + 1))

    return result


def mkdir(connector, id):
    res = zeit.connector.resource.Resource(
        id, None, 'folder', StringIO.StringIO(''),
        contentType='httpd/unix-directory')
    connector.add(res)


def create_folder_structure(connector, testfolder):
    """Create a folder structure for copy/move"""

    def add_folder(id):
        mkdir(connector, u'http://xml.zeit.de/%s/%s' % (testfolder, id))

    def add_file(id):
        id = u'http://xml.zeit.de/%s/%s' % (testfolder, id)
        res = zeit.connector.resource.Resource(
            id, None, 'text', StringIO.StringIO('Pop.'),
            contentType='text/plain')
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

    expected_structure = [x.format(testfolder=testfolder) for x in [
        'http://xml.zeit.de/{testfolder}/testroot',
        'http://xml.zeit.de/{testfolder}/testroot/a/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/a/a/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/a/b/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/a/b/c/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/a/b/c/foo text',
        'http://xml.zeit.de/{testfolder}/testroot/a/f text',
        'http://xml.zeit.de/{testfolder}/testroot/b/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/b/a/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/b/b/ folder',
        'http://xml.zeit.de/{testfolder}/testroot/b/b/foo text',
        'http://xml.zeit.de/{testfolder}/testroot/f text',
        'http://xml.zeit.de/{testfolder}/testroot/g text',
        'http://xml.zeit.de/{testfolder}/testroot/h text']]
    assert expected_structure == list_tree(
        connector, 'http://xml.zeit.de/%s/testroot' % testfolder)


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
        locals[name] = make_delegate(name)
