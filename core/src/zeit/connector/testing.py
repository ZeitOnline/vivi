# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import BTrees
import StringIO
import ZODB.blob
import os
import pkg_resources
import zc.queue.tests
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.connector.mock
import zope.app.testing.functional


zope_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'zope_connector_layer', allow_teardown=True)


real_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting-real.zcml'),
    __name__, 'real_connector_layer', allow_teardown=True)


mock_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting-mock.zcml'),
    __name__, 'mock_connector_layer', allow_teardown=True)


optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
             doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
def realConnector():
    return zeit.connector.connector.Connector(roots={
        "default": os.environ['connector-url'],
        "search": os.environ['search-connector-url']})


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
        reset_testing_folder(self)


class MockTest(ConnectorTest):

    layer = mock_connector_layer

    def setUp(self):
        super(MockTest, self).setUp()
        self.connector._reset()
        self.connector.add(self.get_resource(
            '', '', contentType='httpd/x-unix-directory'))


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', real_connector_layer)
    kw['package'] = 'zeit.connector'
    kw['optionflags'] = optionflags
    kw['setUp'] = reset_testing_folder
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test


def reset_testing_folder(test):
    no_site = object()
    old_site = no_site
    if hasattr(test, 'globs'):
        root = test.globs['getRootFolder']()
        old_site = zope.site.hooks.getSite()
        zope.site.hooks.setSite(root)

    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    for name, uid in connector.listCollection(
        'http://xml.zeit.de/testing/'):
        del connector[uid]

    if old_site is not no_site:
        zope.site.hooks.setSite(old_site)


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
