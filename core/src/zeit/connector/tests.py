# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

from zope.testing import doctest
import StringIO
import os
import random
import thread
import threading
import time
import traceback
import transaction
import unittest
import zeit.connector.cache
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.connector.resource
import zope.app.appsetup.product
import zope.app.component.hooks
import zope.app.testing.functional
import zope.component
import zope.security.proxy


real_connector_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ConnectorLayer', allow_teardown=True)


optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
             doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)


class ThreadingTest(zope.app.testing.functional.FunctionalTestCase):

    layer = real_connector_layer
    level = 3

    def setUp(self):
        """Prepares for a functional test case."""
        super(ThreadingTest, self).setUp()
        self.old_site = zope.app.component.hooks.getSite()
        zope.app.component.hooks.setSite(self.getRootFolder())
        self.connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        transaction.commit()

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        super(ThreadingTest, self).tearDown()
        zope.app.component.hooks.setSite(self.old_site)

    def test_threading(self):
        threads = []
        self.checker = []
        while len(threads) < 10:
            threads.append(threading.Thread(target=self.create_struct))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = [
            '',
            u'/testroot/ folder',
            u'/testroot/a/ folder',
            u'/testroot/a/a/ folder',
            u'/testroot/a/b/ folder',
            u'/testroot/a/b/c/ folder',
            u'/testroot/a/b/c/foo text',
            u'/testroot/a/f text',
            u'/testroot/b/ folder',
            u'/testroot/b/a/ folder',
            u'/testroot/b/b/ folder',
            u'/testroot/b/b/foo text',
            u'/testroot/f text',
            u'/testroot/g text',
            u'/testroot/h text']

        self.assertEquals(10, len(self.checker))
        expected_list = [c for c in self.checker if c != expected]
        self.assertEquals([], expected_list)

    def create_struct(self):
        transaction.abort()
        base = 'http://xml.zeit.de/testing/%s-%s' % (
            str(thread.get_ident()).encode('base64')[:-3], time.time())
        zope.app.component.hooks.setSite(self.getRootFolder())

        def add_folder(id):
            time.sleep(random.uniform(0, 0.2))
            id = u'%s/%s' % (base, id)
            res = zeit.connector.resource.Resource(
                id, None, 'folder', StringIO.StringIO(''),
                contentType = 'httpd/unix-directory')
            self.connector.add(res)
        def add_file(id):
            time.sleep(random.uniform(0, 0.2))
            id = u'%s/%s' % (base, id)
            res = zeit.connector.resource.Resource(
                id, None, 'text', StringIO.StringIO('Pop.'),
                contentType = 'text/plain')
            self.connector.add(res)

        try:
            add_folder('')
            add_folder('testroot')
            add_folder('testroot/a')
            add_folder('testroot/a/a')
            transaction.commit()
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
            transaction.commit()
        except Exception, e:
            traceback.print_exc()
            transaction.abort()

        result = list_tree(self.connector, base)
        self.checker.append([r.replace(base, '') for r in result])
        try:
            del self.connector[base]
        except Exception, e:
            traceback.print_exc()
        transaction.commit()


class ConnectorTest(unittest.TestCase):

    def setUp(self):
        super(ConnectorTest, self).setUp()
        self.connector = zeit.connector.connector.Connector(
            roots={"default": os.environ['connector-url']})

    def tearDown(self):
        for name, uid in self.connector.listCollection(
            'http://xml.zeit.de/testing/'):
            del self.connector[uid]



class TestUnicode(ConnectorTest):

    def test_access(self):
        r = self.connector[
            u'http://xml.zeit.de/online/2007/09/laktose-milchzucker-gewöhnung']

    def test_create_and_list(self):
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.assertEquals(
            [(u'ünicöde', rid)],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))

    def test_overwrite(self):
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Paff'),
            contentType='text/plain')
        self.assertEquals('Paff', self.connector[rid].data.read())


class ConnectorCache(ConnectorTest):

    rid = 'http://xml.zeit.de/testing/cache_test'

    def setUp(self):
        super(ConnectorCache, self).setUp()
        self.connector[self.rid] = zeit.connector.resource.Resource(
            self.rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        list(self.connector.listCollection('http://xml.zeit.de/testing/'))

    def test_deleting_non_existing_resource_does_not_create_cache_entry(self):
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/testing/']
        children.remove(self.rid)
        del self.connector[self.rid]
        self.assertEquals([], list(children))

    def test_delete_updates_cache(self):
        del self.connector[self.rid]
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/testing/']
        self.assertEquals([], list(children))

    def test_cache_time_is_not_stored_on_dav(self):
        key = ('cached-time', 'INTERNAL')
        properties = self.connector[self.rid].properties
        cache_time = properties[key]
        self.connector.changeProperties(self.rid, {key: 'foo'})
        properties = self.connector[self.rid].properties
        self.assertNotEqual('foo', properties[key])
        davres = self.connector._get_dav_resource(self.rid)
        davres.update()
        self.assertTrue(key not in davres.get_all_properties())
        properties = self.connector[self.rid].properties
        self.assertEqual(cache_time, properties[key])

    def test_cache_time_is_not_stored_on_dav_with_add(self):
        key = ('cached-time', 'INTERNAL')
        self.connector.add(self.connector[self.rid])
        davres = self.connector._get_dav_resource(self.rid)
        davres.update()
        self.assertTrue(key not in davres.get_all_properties())

    def test_cache_handles_webdav_keys(self):
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        self.connector.changeProperties(self.rid, {key: 'baz'})

    def test_cache_handles_security_proxied_webdav_keys(self):
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        key = zope.security.proxy.ProxyFactory(key)
        self.connector.changeProperties(self.rid, {key: 'baz'})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'connector.txt',
        'locking.txt',
        'mock.txt',
        'resource.txt',
        'search.txt',
        optionflags=optionflags))
    suite.addTest(unittest.makeSuite(ConnectorCache))
    suite.addTest(unittest.makeSuite(TestUnicode))

    long_running = doctest.DocFileSuite(
        'longrunning.txt',
        'stressing.txt',
        optionflags=optionflags)
    long_running.level = 3
    suite.addTest(long_running)

    functional = zope.app.testing.functional.FunctionalDocFileSuite(
        'cache.txt',
        'functional.txt',
        'invalidator.txt',
        'invalidation-events.txt',
        optionflags=optionflags)
    functional.layer = real_connector_layer
    suite.addTest(functional)

    suite.addTest(unittest.makeSuite(ThreadingTest))

    return suite


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
