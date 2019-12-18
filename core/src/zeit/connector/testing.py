import StringIO
import ZODB.blob
import contextlib
import docker
import os
import pkg_resources
import plone.testing
import pytest
import re
import requests
import socket
import threading
import time
import transaction
import urlparse
import zc.queue.tests
import zeit.cms.testing
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.connector.mock
import zope.component.hooks
import zope.testing.renormalizing


class DAVServerLayer(plone.testing.Layer):

    def setUp(self):
        dav = self.get_random_port()
        query = self.get_random_port()
        client = docker.from_env()
        self['dav_container'] = client.containers.run(
            "registry.zeit.de/dav-server:1.1.0", detach=True, remove=True,
            ports={9000: dav, 9999: query})
        self['dav_url'] = 'http://localhost:%s/cms/' % dav
        self['query_url'] = 'http://localhost:%s' % query
        self.wait_for_http(self['dav_url'])
        # self.wait_for_http(self['query_url'])
        TBC = zeit.connector.connector.TransactionBoundCachingConnector
        self['connector'] = TBC({'default': self['dav_url']})
        mkdir(self['connector'], 'http://xml.zeit.de/testing')

    def tearDown(self):
        self['dav_container'].stop()
        del self['dav_container']
        del self['dav_url']
        del self['query_url']
        del self['connector']

    # Taken from pytest-nginx
    def get_random_port(self):
        s = socket.socket()
        with contextlib.closing(s):
            s.bind(('localhost', 0))
            return s.getsockname()[1]

    def wait_for_http(self, url, timeout=5, sleep=0.2):
        slept = 0
        while slept < timeout:
            try:
                requests.get(url, timeout=1)
            except Exception:
                pass
            else:
                return
        raise TimeoutError('%s did not start up' % url)

    def testTearDown(self):
        transaction.abort()
        connector = self['connector']
        for name, uid in connector.listCollection(
                'http://xml.zeit.de/testing'):
            connector.unlock(uid)
            del connector[uid]

        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.connections = threading.local()


DAV_SERVER_LAYER = DAVServerLayer()


class ConfigLayer(zeit.cms.testing.ProductConfigLayer):

    defaultBases = (DAV_SERVER_LAYER,)

    def setUp(self):
        self.config = {
            'document-store': self['dav_url'],
            'document-store-search': self['query_url'],
        }
        super(ConfigLayer, self).setUp()


DAV_CONFIG_LAYER = ConfigLayer({})

ZOPE_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', bases=(DAV_CONFIG_LAYER, zeit.cms.testing.CONFIG_LAYER))
ZOPE_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZOPE_ZCML_LAYER,))

REAL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting-real.zcml',
    bases=(DAV_CONFIG_LAYER, zeit.cms.testing.CONFIG_LAYER))
REAL_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(bases=(REAL_ZCML_LAYER,))


FILESYSTEM_CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {'repository-path': pkg_resources.resource_filename(
        'zeit.connector', 'testcontent')})
FILESYSTEM_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting-filesystem.zcml',
    bases=(FILESYSTEM_CONFIG_LAYER, zeit.cms.testing.CONFIG_LAYER))
FILESYSTEM_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(
    bases=(FILESYSTEM_ZCML_LAYER,))

MOCK_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting-mock.zcml', bases=(zeit.cms.testing.CONFIG_LAYER,))
MOCK_CONNECTOR_LAYER = zeit.cms.testing.ZopeLayer(bases=(MOCK_ZCML_LAYER,))


class TestCase(zeit.cms.testing.FunctionalTestCase):

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)

    # XXX I'm not sure this is still useful now that we use a container
    @property
    def testfolder(self):
        return self.layer.get('testfolder', 'testing')

    def get_resource(self, name, body, properties={},
                     contentType='text/plain'):
        rid = 'http://xml.zeit.de/%s/%s' % (self.testfolder, name)
        return zeit.connector.resource.Resource(
            rid, name, 'testing',
            StringIO.StringIO(body),
            properties=properties,
            contentType=contentType)


@pytest.mark.slow
class ConnectorTest(TestCase):

    layer = REAL_CONNECTOR_LAYER
    level = 2


class FilesystemConnectorTest(TestCase):

    layer = FILESYSTEM_CONNECTOR_LAYER


class MockTest(TestCase):

    layer = MOCK_CONNECTOR_LAYER

    def setUp(self):
        super(MockTest, self).setUp()
        # I don't really get what this is here for, but removing it breaks
        # tests:
        self.connector.add(self.get_resource(
            '', '', contentType='httpd/x-unix-directory'))


def FunctionalDocFileSuite(*paths, **kw):
    kw['package'] = 'zeit.connector'
    kw['globs'] = {
        'TESTFOLDER': lambda: kw['layer'].get('testfolder', 'testing')}
    return zeit.cms.testing.FunctionalDocFileSuite(*paths, **kw)


def mark_doctest_suite(suite, mark):
    # Imitate pytest magic, see _pytest.python.transfer_markers
    for test in suite:
        func = test.runTest.im_func
        mark(func)
        test.runTest = func.__get__(test)


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
