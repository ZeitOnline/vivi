# coding: utf8
from io import BytesIO
import os
import tempfile
import threading

import BTrees
import pytest
import transaction
import zc.queue.tests
import ZODB

import zeit.cms.testing
import zeit.connector.cache
import zeit.connector.testing


class TestResourceCache(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.connector.testing.ZOPE_DAV_CONNECTOR_LAYER

    def setUp(self):
        super().setUp()
        self.cache = zeit.connector.cache.ResourceCache()
        self.getRootFolder()['cache'] = self.cache
        self.uniqueId = 'föö'
        self.key = zeit.connector.cache.get_storage_key(self.uniqueId)
        self.BUFFER_SIZE = zeit.connector.cache.Body().BUFFER_SIZE

    def test_etag_migration(self):
        self.cache._etags = BTrees.family64.OO.BTree()
        self.cache._etags[self.key] = 'etag1'
        data = zeit.connector.cache.SlottedStringRef(b'data')
        self.cache._data[self.key] = data
        got = self.cache.getData(self.uniqueId, 'etag1')
        self.assertEqual(b'data', got.read())
        got.close()
        del self.cache._etags[self.key]
        self.assertRaises(KeyError, self.cache.getData, self.uniqueId, 'etag1')
        del self.cache._etags
        self.assertRaises(KeyError, self.cache.getData, self.uniqueId, 'etag1')

    def test_missing_blob_file(self):
        body1 = self.BUFFER_SIZE * 2 * b'x'
        data1 = BytesIO(body1)
        body2 = self.BUFFER_SIZE * 2 * b'y'
        data2 = BytesIO(body2)
        self.cache.setData(self.uniqueId, data1, 'etag1').close()
        transaction.commit()
        body = self.cache._data[self.key]
        os.remove(body.data.committed())
        del body.data._p_changed  # Invalidate, thus force reload
        self.assertRaises(KeyError, self.cache.getData, self.uniqueId, 'etag1')
        self.cache.setData(self.uniqueId, data2, 'etag2').close()
        got = self.cache.getData(self.uniqueId, 'etag2')
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
        self.assertRaises(KeyError, self.cache.getData, self.uniqueId, 'etag1')
        expected = self.BUFFER_SIZE * 2 * b'y'
        data2 = BytesIO(expected)
        self.cache.setData(self.uniqueId, data2, 'etag2').close()
        got = self.cache.getData(self.uniqueId, 'etag2')
        self.assertEqual(expected, got.read())
        got.close()

    @pytest.mark.xfail()
    def test_blob_conflict_resolution(self):
        body = BytesIO(b'body' * self.BUFFER_SIZE)

        def store():
            transaction.abort()
            self.cache.setData(self.uniqueId, body, 'etag1').close()
            transaction.commit()

        t1 = threading.Thread(target=store)
        t2 = threading.Thread(target=store)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def test_no_etag_conflict_resolution(self):
        """The SQL connector does not use etag, so conflicts always result in 'not cached'"""
        # This is not part of cache.txt because doctests have bad isolation,
        # and "simply" appending it does not work.
        blob_dir = tempfile.mkdtemp()
        storage = zc.queue.tests.ConflictResolvingMappingStorage('test')
        storage = ZODB.blob.BlobStorage(blob_dir, storage)
        db = ZODB.DB(storage)
        transactionmanager_1 = transaction.TransactionManager()
        transactionmanager_2 = transaction.TransactionManager()
        connection_1 = db.open(transaction_manager=transactionmanager_1)
        root_1 = connection_1.root()
        c_1 = root_1['cache'] = zeit.connector.cache.ResourceCache()

        body = b'A small file' * self.BUFFER_SIZE
        c_1.update('id', BytesIO(body)).close()
        transactionmanager_1.commit()

        connection_2 = db.open(transaction_manager=transactionmanager_2)
        root_2 = connection_2.root()
        c_2 = root_2['cache']

        body1 = BytesIO(b'Body 1' * self.BUFFER_SIZE)
        body2 = BytesIO(b'Body 2' * self.BUFFER_SIZE)
        c_1.update('id', body1).close()
        c_2.update('id', body2).close()
        transactionmanager_2.commit()
        transactionmanager_1.commit()
        connection_1.sync()
        connection_2.sync()
        with self.assertRaises(KeyError):
            c_1['id']
        with self.assertRaises(KeyError):
            c_2['id']
