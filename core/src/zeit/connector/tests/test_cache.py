# coding: utf8
from io import BytesIO
import BTrees
import ZODB
import pytest
import os
import threading
import transaction
import zeit.cms.testing
import zeit.connector.cache
import zeit.connector.testing


class TestResourceCache(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.connector.testing.ZOPE_CONNECTOR_LAYER

    def setUp(self):
        super().setUp()
        self.cache = zeit.connector.cache.ResourceCache()
        self.getRootFolder()['cache'] = self.cache
        self.properties1 = {('getetag', 'DAV:'): 'etag1'}
        self.properties2 = {('getetag', 'DAV:'): 'etag2'}
        self.uniqueId = 'föö'
        self.key = zeit.connector.cache.get_storage_key(self.uniqueId)
        self.BUFFER_SIZE = zeit.connector.cache.Body.BUFFER_SIZE

    def test_etag_migration(self):
        self.cache._etags = BTrees.family64.OO.BTree()
        self.cache._etags[self.key] = 'etag1'
        data = zeit.connector.cache.SlottedStringRef(b'data')
        self.cache._data[self.key] = data
        got = self.cache.getData(self.uniqueId, self.properties1)
        self.assertEqual(b'data', got.read())
        got.close()
        del self.cache._etags[self.key]
        self.assertRaises(
            KeyError, self.cache.getData, self.uniqueId, self.properties1)
        del self.cache._etags
        self.assertRaises(
            KeyError, self.cache.getData, self.uniqueId, self.properties1)

    def test_missing_blob_file(self):
        body1 = self.BUFFER_SIZE * 2 * b'x'
        data1 = BytesIO(body1)
        body2 = self.BUFFER_SIZE * 2 * b'y'
        data2 = BytesIO(body2)
        self.cache.setData(self.uniqueId, self.properties1, data1).close()
        transaction.commit()
        body = self.cache._data[self.key]
        os.remove(body.data.committed())
        del body.data._p_changed  # Invalidate, thus force reload
        self.assertRaises(KeyError,
                          self.cache.getData, self.uniqueId, self.properties1)
        self.cache.setData(self.uniqueId, self.properties2, data2).close()
        got = self.cache.getData(self.uniqueId, self.properties2)
        self.assertEqual(body2, got.read())
        got.close()

    def test_missing_blob_file_with_legacy_data(self):
        data = ZODB.blob.Blob()
        with data.open('w') as f:
            f.write(b'ablob')
        self.cache._data[self.key] = data
        self.cache._etags = BTrees.family64.OO.BTree()
        self.cache._etags[self.key] = 'etag1'
        transaction.commit()
        os.remove(data.committed())
        del data._p_changed
        self.assertRaises(KeyError,
                          self.cache.getData, self.uniqueId, self.properties1)
        expected = self.BUFFER_SIZE * 2 * b'y'
        data2 = BytesIO(expected)
        self.cache.setData(self.uniqueId, self.properties2, data2).close()
        got = self.cache.getData(self.uniqueId, self.properties2)
        self.assertEqual(expected, got.read())
        got.close()

    @pytest.mark.xfail
    def test_blob_conflict_resolution(self):
        size = zeit.connector.cache.Body.BUFFER_SIZE
        body = BytesIO(b'body' * size)

        def store():
            transaction.abort()
            self.cache.setData(self.uniqueId, self.properties1, body).close()
            transaction.commit()
        t1 = threading.Thread(target=store)
        t2 = threading.Thread(target=store)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
