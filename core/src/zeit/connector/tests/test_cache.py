from io import BytesIO

from pendulum import datetime
import time_machine
import transaction

import zeit.connector.cache
import zeit.connector.testing


class AccessTimeTest(zeit.connector.testing.MockTest):
    def setUp(self):
        super().setUp()
        self.cache = zeit.connector.cache.ResourceCache()

    def make_value(self):
        return BytesIO(b'body')

    def test_reading_updates_cache_access(self):
        self.assertEqual([], list(self.cache._access_time_by_id.items()))
        self.assertEqual([], list(self.cache._sorted_access_time.items()))
        with time_machine.travel(datetime(2012, 6, 12)):
            self.cache.update('some-id', self.make_value()).close()
        self.assertEqual([('some-id', 20120612)], list(self.cache._access_time_by_id.items()))
        self.assertEqual([('20120612_some-id', 1)], list(self.cache._sorted_access_time.items()))

    def test_same_cache_access_causes_no_zodb_change(self):
        self.getRootFolder()['cache'] = self.cache
        transaction.commit()
        with time_machine.travel(datetime(2012, 6, 12)):
            self.cache.update('some-id', self.make_value()).close()
            transaction.commit()
            self.cache['some-id'].close()
            self.assertFalse(self.cache._data._p_changed)
            self.assertFalse(self.cache._access_time_by_id._p_changed)
            self.assertFalse(self.cache._sorted_access_time._p_changed)
            transaction.abort()
        with time_machine.travel(datetime(2012, 6, 13)):
            self.cache['some-id'].close()
            self.assertFalse(self.cache._data._p_changed)
            self.assertTrue(self.cache._access_time_by_id._p_changed)
            self.assertTrue(self.cache._sorted_access_time._p_changed)

    def test_sweep_removes_old_entries(self):
        with time_machine.travel(datetime(2012, 6, 12)):
            self.cache.update('id1', self.make_value()).close()
            self.cache.update('id2', self.make_value()).close()
        with time_machine.travel(datetime(2012, 6, 13)):
            self.cache.update('id3', self.make_value()).close()
            self.cache.update('id4', self.make_value()).close()
        with time_machine.travel(datetime(2012, 6, 14)):
            self.cache.sweep(1)
            self.assertNotIn('id1', self.cache)
            self.assertNotIn('id2', self.cache)
            self.assertIn('id3', self.cache)
            self.assertIn('id4', self.cache)
        self.assertEqual(['id3', 'id4'], list(self.cache._data))
        self.assertEqual(['id3', 'id4'], list(self.cache._access_time_by_id))
        self.assertEqual(['20120614_id3', '20120614_id4'], list(self.cache._sorted_access_time))
