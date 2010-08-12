# coding: utf8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import StringIO
import ZODB
import os
import threading
import transaction
import zeit.connector.cache
import zeit.connector.testing
import zope.app.testing.functional


class TestResourceCache(zope.app.testing.functional.FunctionalTestCase):

    layer = zeit.connector.testing.zope_connector_layer

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
