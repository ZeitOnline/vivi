from datetime import datetime, timedelta
from io import BytesIO
from unittest import mock

from sqlalchemy import func, select
from sqlalchemy import text as sql
from sqlalchemy.exc import IntegrityError
import google.api_core.exceptions
import pytz
import transaction

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.cms.repository.interfaces import ConflictError
from zeit.connector.interfaces import INTERNAL_PROPERTY
from zeit.connector.models import Lock
from zeit.connector.postgresql import _unlock_overdue_locks
from zeit.connector.resource import Resource, WriteableCachedResource
from zeit.connector.search import SearchVar
from zeit.workflow.interfaces import WORKFLOW_NS
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
        self.assertEqual('foo', props.name)
        self.assertEqual('/testing', props.parent_path)
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

    def test_updates_type_from_dav_property(self):
        res = self.get_resource('foo')
        self.connector.add(res)
        self.connector.changeProperties(
            res.id, {('type', 'http://namespaces.zeit.de/CMS/meta'): 'changed'}
        )
        res = self.connector[res.id]
        self.assertEqual('changed', res.type)

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

    def test_search_for_uuid_uses_indexed_column(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        UUID = SearchVar('uuid', 'http://namespaces.zeit.de/CMS/document')
        result = self.connector.search([UUID], UUID == props.id)
        unique_id, uuid = next(result)
        self.assertEqual(res.id, unique_id)
        self.assertEqual('{urn:uuid:%s}' % props.id, uuid)

    def test_search_by_sql_applies_query(self):
        res = self.add_resource('one', type='article')
        self.add_resource('two', type='centerpage')
        query = self.connector.query()
        query = query.filter_by(type='article')
        result = self.connector.search_sql(query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, res.id)

    def test_search_by_sql_uses_cache(self):
        self.add_resource('one', body=b'mybody', type='article')
        query = self.connector.query()
        query = query.filter_by(type='article')
        result = self.connector.search_sql(query)
        with mock.patch.object(
            self.connector.session, 'execute', side_effect=RuntimeError('disabled')
        ):
            self.assertEqual(result[0].data.read(), b'mybody')

    def test_search_sql_count_returns_result_count(self):
        self.add_resource('one', type='article')
        self.add_resource('two', type='centerpage')
        self.add_resource('three', type='article')
        query = self.connector.query()
        query = query.filter_by(type='article')
        self.assertEqual(self.connector.search_sql_count(query), 2)

    def test_search_sql_suppresses_errors(self):
        self.connector.session.execute(sql('set statement_timeout=1'))
        query = self.connector.query().add_columns(sql('pg_sleep(1)'))
        result = self.connector.search_sql(query)
        self.assertEqual(len(result), 0)
        # Ensure no InFailedSqlTransaction exception happens on subsequent calls
        result = self.connector.search_sql(self.connector.query())
        self.assertEqual(len(result), 1)

    def test_search_sql_count_suppresses_errors(self):
        self.connector.session.execute(sql('set statement_timeout=1'))
        query = self.connector.query()
        with mock.patch('sqlalchemy.func.count') as count:
            count.return_value = sql('count(*), pg_sleep(1)')
            self.assertEqual(0, self.connector.search_sql_count(query))
        # Ensure no InFailedSqlTransaction exception happens on subsequent calls
        self.assertEqual(1, self.connector.search_sql_count(query))

    def test_search_returns_uuid(self):
        res = self.get_resource(
            'foo',
            b'mybody',
            {
                ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
            },
        )
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        UUID = SearchVar('uuid', 'http://namespaces.zeit.de/CMS/document')
        FOO = SearchVar('foo', 'http://namespaces.zeit.de/CMS/testing')
        result = self.connector.search([UUID, FOO], FOO == 'foo')
        unique_id, uuid, foo = next(result)
        self.assertEqual(res.id, unique_id)
        self.assertEqual('{urn:uuid:%s}' % props.id, uuid)
        self.assertEqual('foo', foo)

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
        Content, to prevent accidental deletions of locked content when
        operating directly on the DB."""
        self._create_lock(1)
        content = self.connector._get_content('http://xml.zeit.de/testing/foo-1')
        with self.assertRaises(IntegrityError):
            self.connector.session.execute(
                sql('DELETE FROM properties WHERE id=:id'), {'id': content.id}
            )
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

    def test_lock_with_missing_timeout(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        self.connector.lock(res.id, 'someone', None)
        transaction.commit()
        lock_status = self.connector.locked(res.id)
        now = datetime.now(pytz.UTC)
        self.assertGreaterEqual(lock_status[1], now)

    def test_lock_update_relationship(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        self.connector.lock(res.id, 'someone', None)
        content = self.connector._get_content(res.id)
        stmt = select(Lock).where(Lock.id == content.id)
        lock = self.connector.session.scalars(stmt).one()
        self.assertEqual('someone', lock.principal)
        self.assertEqual(lock, content.lock)


class ContractChecksum(zeit.connector.testing.SQLTest):
    NS = 'http://namespaces.zeit.de/CMS/testing'
    CHECK_PROPERTY = ('body_checksum', INTERNAL_PROPERTY)

    def test_setitem_generates_checksum(self):
        res = self.add_resource('foo', body=b'cookies')
        self.assertNotEqual(None, res.properties[self.CHECK_PROPERTY])

    def test_empty_body_has_empty_checksum(self):
        res = self.add_resource('foo', body=b'')
        self.assertEqual(None, res.properties[self.CHECK_PROPERTY])

    def test_conflicting_writes(self):
        self.connector.add(
            self.get_resource('foo', body=b'cookies', properties={self.CHECK_PROPERTY: '1'})
        )
        with self.assertRaises(ConflictError):
            self.connector.add(
                self.get_resource('foo', body=b'cake', properties={self.CHECK_PROPERTY: '2'})
            )

    def test_collection_has_empty_checksum(self):
        self.mkdir('folder')
        folder = self.connector['http://xml.zeit.de/testing/folder']
        self.assertEqual(None, folder.properties[self.CHECK_PROPERTY])

    def test_binary_has_empty_checksum(self):
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector.add(res)
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual(None, res.properties[self.CHECK_PROPERTY])


class PropertiesColumnTest(zeit.connector.testing.SQLTest):
    layer = zeit.connector.testing.SQL_CONTENT_LAYER

    def test_properties_can_be_stored_in_separate_columns(self):
        FEATURE_TOGGLES.set('write_metadata_columns', True)
        FEATURE_TOGGLES.set('read_metadata_columns', True)
        res = self.add_resource('foo', properties={('access', DOCUMENT_SCHEMA_NS): 'foo'})
        self.assertEqual('foo', res.properties[('access', DOCUMENT_SCHEMA_NS)])
        content = self.connector._get_content(res.id)
        self.assertEqual('foo', content.access)

    def test_search_looks_in_columns_or_unsorted_depending_on_toggle(self):
        FEATURE_TOGGLES.set('write_metadata_columns', True)

        res = self.add_resource('foo', properties={('access', DOCUMENT_SCHEMA_NS): 'foo'})
        access = SearchVar('access', 'http://namespaces.zeit.de/CMS/document')
        for toggle in [False, True]:  # XXX parametrize would be nice
            FEATURE_TOGGLES.set('read_metadata_columns', toggle)
            if toggle:
                self.connector._get_content(res.id).unsorted = {}
                transaction.commit()
            result = self.connector.search([access], access == 'foo')
            unique_id, uuid = next(result)
            self.assertEqual(res.id, unique_id)


class WorkflowColumnsTest(zeit.connector.testing.SQLTest):
    layer = zeit.connector.testing.SQL_CONTENT_LAYER

    TIMESTAMP = '2024-05-21T12:53:20.880753+00:00'
    EXPECTED_DATETIME = datetime(2024, 5, 21, 12, 53, 20, 880753, pytz.UTC)

    def setUp(self):
        super().setUp()
        FEATURE_TOGGLES.set('read_metadata_columns', True)
        FEATURE_TOGGLES.set('write_metadata_columns', True)

    def _make_resource(self, properties):
        res = self.add_resource('foo', properties=properties)
        return self.connector._get_content(res.id)

    def test_date_created(self):
        properties = {('date_created', DOCUMENT_SCHEMA_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_created, self.EXPECTED_DATETIME)

    def test_date_first_released(self):
        properties = {('date_first_released', DOCUMENT_SCHEMA_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_first_released, self.EXPECTED_DATETIME)

    def test_date_last_checkout(self):
        properties = {('date_last_checkout', DOCUMENT_SCHEMA_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_last_checkout, self.EXPECTED_DATETIME)

    def test_date_last_modified_semantic(self):
        properties = {('last-semantic-change', DOCUMENT_SCHEMA_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_last_modified_semantic, self.EXPECTED_DATETIME)

    def test_date_last_published(self):
        properties = {('date_last_published', WORKFLOW_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_last_published, self.EXPECTED_DATETIME)

    def test_date_last_published_semantic(self):
        properties = {
            (
                'date_last_published_semantic',
                WORKFLOW_NS,
            ): self.TIMESTAMP
        }
        content = self._make_resource(properties)
        self.assertEqual(content.date_last_published_semantic, self.EXPECTED_DATETIME)

    def test_date_print_published(self):
        properties = {('print-publish', DOCUMENT_SCHEMA_NS): self.TIMESTAMP}
        content = self._make_resource(properties)
        self.assertEqual(content.date_print_published, self.EXPECTED_DATETIME)
