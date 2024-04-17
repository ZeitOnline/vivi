from datetime import datetime, timedelta
from io import BytesIO
from unittest import mock

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
import google.api_core.exceptions
import pytz
import transaction

from zeit.connector.postgresql import Lock, _unlock_overdue_locks
from zeit.connector.resource import Resource, WriteableCachedResource
from zeit.connector.search import SearchVar
import zeit.connector.testing


class SQLConnectorTest(zeit.connector.testing.SQLTest):
    def test_serializes_properties_as_json(self):
        res = self.get_resource(
            'foo',
            b'mybody',
            {
                (
                    'uuid',
                    'http://namespaces.zeit.de/CMS/document',
                ): '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}',
                ('foo', 'http://namespaces.zeit.de/CMS/one'): 'foo',
                ('bar', 'http://namespaces.zeit.de/CMS/two'): 'bar',
            },
        )
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        self.assertEqual('foo', props.path.name)
        self.assertEqual('/testing', props.path.parent_path)
        self.assertEqual('testing', props.type)
        self.assertEqual(False, props.is_collection)
        self.assertEqual('deadbeaf-c5aa-4232-837a-ae6701270436', props.id)
        self.assertEqual(
            {
                'document': {'uuid': '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}'},
                'one': {'foo': 'foo'},
                'two': {'bar': 'bar'},
            },
            props.unsorted,
        )

    def test_stores_body_in_gcs_for_configured_binary_content_types(self):
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        blob = self.connector.bucket.blob(props.id)
        self.assertEqual(b'mybody', blob.download_as_bytes())

    def test_empty_body_does_not_break(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        props.body = None  # Not quite clear how this happens in production
        transaction.commit()
        res = self.connector[res.id]
        self.assertEqual(b'', res.data.read())

    def test_injects_uuid_and_type_into_dav_properties(self):
        res = self.get_resource(
            'foo',
            b'mybody',
            {
                ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
            },
        )
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        davprops = props.to_webdav()
        self.assertEqual(
            '{urn:uuid:%s}' % props.id, davprops[('uuid', 'http://namespaces.zeit.de/CMS/document')]
        )
        self.assertEqual('testing', davprops[('type', 'http://namespaces.zeit.de/CMS/meta')])

    def test_provides_last_updated_column(self):
        # Properly we would test that the value of the last_updated column
        # increases on INSERT and UPDATE. But our test setup wraps everything
        # in an outer transaction, which causes any SQL `NOW()` calls to return
        # the start time of that transaction -- so we cannot detect an increase
        res = self.get_resource('foo')
        self.connector.add(res)
        transaction.commit()
        props = self.connector._get_content(res.id)
        self.assertIsInstance(props.last_updated, datetime)

    def test_determines_size_for_gcs_upload(self):
        body = b'mybody'
        for res in [
            Resource('http://xml.zeit.de/testing/foo', 'foo', 'file', BytesIO(body), {}),
            WriteableCachedResource(
                'http://xml.zeit.de/testing/foo',
                'foo',
                'file',
                lambda: {},
                lambda: BytesIO(body),
                is_collection=False,
            ),
        ]:
            self.connector.add(res)
            props = self.connector._get_content(res.id)
            blob = self.connector.bucket.blob(props.id)
            self.assertEqual(body, blob.download_as_bytes())

    def test_delete_removes_gcs_blob(self):
        collection_id = 'http://xml.zeit.de/testing/folder'
        zeit.connector.testing.mkdir(self.connector, collection_id)
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector['http://xml.zeit.de/testing/folder/foo'] = res
        props = self.connector._get_content(res.id)
        blob = self.connector.bucket.blob(props.id)
        del self.connector[collection_id]
        with self.assertRaises(google.api_core.exceptions.NotFound):
            blob.download_as_bytes()

    def test_delete_ignores_nonexistent_gcs_blob(self):
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        blob = self.connector.bucket.blob(props.id)
        blob.delete()
        with self.assertNothingRaised():
            del self.connector[res.id]

    def test_delete_removes_rows_from_all_tables(self):
        from zeit.connector.postgresql import Content, Path

        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        uuid = props.id
        del self.connector[res.id]
        transaction.commit()
        self.assertEqual(None, self.connector.session.get(Path, self.connector._pathkey(res.id)))
        self.assertEqual(None, self.connector.session.get(Content, uuid))

    def test_search_for_uuid_uses_indexed_column(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        UUID = SearchVar('uuid', 'http://namespaces.zeit.de/CMS/document')
        result = self.connector.search([UUID], UUID == props.id)
        unique_id, uuid = next(result)
        self.assertEqual(res.id, unique_id)
        self.assertEqual(props.id, uuid)

    def test_copy_duplicates_gcs_blob(self):
        source = self.get_resource('foo', b'mybody')
        source.type = 'file'
        target = self.get_resource('bar')
        self.connector.add(source)
        self.connector.copy(source.id, target.id)

        source_props = self.connector._get_content(source.id)
        source_blob = self.connector.bucket.blob(source_props.id)

        target_props = self.connector._get_content(target.id)
        target_blob = self.connector.bucket.blob(target_props.id)

        self.assertNotEqual(source_props.id, target_props.id)
        self.assertNotEqual(source_blob, target_blob)
        self.assertEqual(source_props.type, target_props.type)
        self.assertEqual(source_blob.download_as_bytes(), target_blob.download_as_bytes())

    def test_move_does_not_affect_gcs_blob(self):
        source = self.get_resource('foo', b'mybody')
        source.type = 'file'
        target = self.get_resource('bar')
        self.connector.add(source)
        source_props = self.connector._get_content(source.id)
        source_blob = self.connector.bucket.blob(source_props.id)
        self.connector.move(source.id, target.id)
        target_props = self.connector._get_content(target.id)
        target_blob = self.connector.bucket.blob(target_props.id)
        self.assertEqual(source_props.id, target_props.id)
        self.assertEqual(source_blob.name, target_blob.name)

    def test_regression_delitem_only_checks_locked_children_not_siblings(self):
        self.mkdir('folder')
        res = self.add_resource('foo')
        self.connector.lock(res.id, 'external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertNothingRaised():
            del self.connector['http://xml.zeit.de/testing/folder']

    def _create_lock(self, minutes):
        res = self.get_resource(f'foo-{minutes}', b'mybody')
        self.connector.add(res)
        until = datetime.now(pytz.UTC) + timedelta(minutes=minutes)
        self.connector.lock(res.id, 'someone', until)

    def test_unlock_overdue_locks(self):
        self._create_lock(5)
        self._create_lock(-10)
        assert self.connector.session.scalar(select(func.count(Lock.id))) == 2
        _unlock_overdue_locks()
        assert self.connector.session.scalar(select(func.count(Lock.id))) == 1

    def test_delete_content_with_lock_raises(self):
        """We intentionally have not declared `ON DELETE CASCADE` from Lock to
        Content (there is one for Path though), to prevent accidental deletions
        of locked content when operating directly on the DB.
        """
        self._create_lock(1)
        content = self.connector._get_content('http://xml.zeit.de/testing/foo-1')
        self.connector.session.delete(content)
        with self.assertRaises(IntegrityError):
            transaction.commit()

    def test_locking_can_be_disabled_by_config(self):
        self._create_lock(1)
        transaction.commit()  # clear cache
        with mock.patch.object(self.connector, 'support_locking', new=False):
            self.assertEqual(None, self.connector.locked('http://xml.zeit.de/testing/foo-1')[0])
        transaction.abort()
        self.assertNotEqual(None, self.connector.locked('http://xml.zeit.de/testing/foo-1')[0])

    def test_invalidate_cache_of_nonexistent_content_creates_no_cache(self):
        self.assertNotIn('http://xml.zeit.de/testing/foo', self.connector.child_name_cache)
        self.connector.invalidate_cache('http://xml.zeit.de/testing/foo/bar')
        self.assertNotIn('http://xml.zeit.de/testing/foo', self.connector.child_name_cache)
