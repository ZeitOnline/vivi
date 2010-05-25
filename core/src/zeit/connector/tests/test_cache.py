# coding: utf8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

import BTrees
import StringIO
import ZODB
import os
import threading
import transaction
import zeit.connector.cache
import zeit.connector.resource
import zeit.connector.testing
import zope.app.testing.functional
import zope.security.proxy



class ConnectorCache(zeit.connector.testing.ConnectorTest):

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

    def test_cache_does_not_store_security_proxied_webdav_keys(self):
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        key = zope.security.proxy.ProxyFactory(key)
        self.connector.property_cache['id'] = {key: 'baz'}
        self.assertTrue(isinstance(
            self.connector.property_cache['id'].keys()[0],
            zeit.connector.cache.WebDAVPropertyKey))

    def test_inconsistent_child_names_do_not_yields_non_existing_objects(self):
        self.assertEquals(
            [(u'cache_test', u'http://xml.zeit.de/testing/cache_test')],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))
        cache = self.connector.child_name_cache['http://xml.zeit.de/testing/']
        self.assertEquals(
            [u'http://xml.zeit.de/testing/cache_test'],
            list(cache))
        cache.add('http://xml.zeit.de/testing/cache_test_2')
        self.assertEquals(
            [(u'cache_test', u'http://xml.zeit.de/testing/cache_test')],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))


class TestResourceCache(zope.app.testing.functional.FunctionalTestCase):

    layer = zeit.connector.testing.real_connector_layer

    def setUp(self):
        super(TestResourceCache, self).setUp()
        self.cache = zeit.connector.cache.ResourceCache()
        self.getRootFolder()['cache'] = self.cache
        self.properties1 = {('getetag', 'DAV:'): 'etag1'}
        self.properties2 = {('getetag', 'DAV:'): 'etag2'}
        self.uniqueId = u'föö'
        self.key = zeit.connector.cache.get_storage_key(self.uniqueId)
        self.BUFFER_SIZE = zeit.connector.cache.Body.BUFFER_SIZE

    def test_etag_migration(self):
        self.cache._etags = BTrees.family64.OO.BTree()
        self.cache._etags[self.key] = 'etag1'
        data = zeit.connector.cache.SlottedStringRef('data')
        self.cache._data[self.key] = data
        self.assertEquals(
            'data',
            self.cache.getData(self.uniqueId, self.properties1).read())
        del self.cache._etags[self.key]
        self.assertRaises(KeyError,
            self.cache.getData, self.uniqueId, self.properties1)
        del self.cache._etags
        self.assertRaises(KeyError,
            self.cache.getData, self.uniqueId, self.properties1)

    def test_missing_blob_file(self):
        data1 = StringIO.StringIO(self.BUFFER_SIZE*2*'x')
        data2 = StringIO.StringIO(self.BUFFER_SIZE*2*'y')
        self.cache.setData(self.uniqueId, self.properties1, data1)
        transaction.commit()
        body = self.cache._data[self.key]
        os.remove(body.data.committed())
        del body.data._p_changed  # Invalidate, thus force reload
        self.assertRaises(KeyError,
                          self.cache.getData, self.uniqueId, self.properties1)
        self.cache.setData(self.uniqueId, self.properties2, data2)
        self.assertEquals(
            data2.getvalue(),
            self.cache.getData(self.uniqueId, self.properties2).read())

    def test_missing_blob_file_with_legacy_data(self):
        data = ZODB.blob.Blob()
        data.open('w').write('ablob')
        self.cache._data[self.key] = data
        self.cache._etags = BTrees.family64.OO.BTree()
        self.cache._etags[self.key] = 'etag1'
        transaction.commit()
        os.remove(data.committed())
        del data._p_changed
        self.assertRaises(KeyError,
                          self.cache.getData, self.uniqueId, self.properties1)
        data2 = StringIO.StringIO(self.BUFFER_SIZE*2*'y')
        self.cache.setData(self.uniqueId, self.properties2, data2)
        self.assertEquals(
            data2.getvalue(),
            self.cache.getData(self.uniqueId, self.properties2).read())

    def test_blob_conflict_resolution(self):
        size = zeit.connector.cache.Body.BUFFER_SIZE
        body = StringIO.StringIO('body' * size)
        def store():
            transaction.abort()
            self.cache.setData(self.uniqueId, self.properties1, body)
            transaction.commit()
        t1 = threading.Thread(target=store)
        t2 = threading.Thread(target=store)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
