from io import BytesIO
from unittest import mock
import datetime

from pytest import raises
from sqlalchemy import func, select
from sqlalchemy import text as sql
from sqlalchemy.exc import IntegrityError
import google.api_core.exceptions
import pendulum
import transaction

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.repository.interfaces import ConflictError
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IModified
from zeit.connector.interfaces import INTERNAL_PROPERTY, DeleteProperty
from zeit.connector.models import Content, Lock
from zeit.connector.postgresql import _unlock_overdue_locks
from zeit.connector.resource import Resource, WriteableCachedResource
from zeit.connector.search import SearchVar
import zeit.connector.testing


NS = 'http://namespaces.zeit.de/CMS/'


class SQLConnectorTest(zeit.connector.testing.SQLTest):
    def test_serializes_properties_as_json(self):
        res = self.get_resource(
            'foo',
            b'mybody',
            {
                ('uuid', f'{NS}document'): '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}',
                ('foo', f'{NS}one'): 'foo',
                ('bar', f'{NS}two'): 'bar',
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
        res = self.get_resource('foo', b'mybody', {('foo', f'{NS}testing'): 'foo'})
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        davprops = props.to_webdav()
        self.assertEqual('{urn:uuid:%s}' % props.id, davprops[('uuid', f'{NS}document')])
        self.assertEqual('testing', davprops[('type', f'{NS}meta')])

    def test_updates_type_from_dav_property(self):
        res = self.get_resource('foo')
        self.connector.add(res)
        self.connector.changeProperties(res.id, {('type', f'{NS}meta'): 'changed'})
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
        self.assertIsInstance(props.last_updated, datetime.datetime)

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
        UUID = SearchVar('uuid', f'{NS}document')
        result = self.connector.search([UUID], UUID == props.id)
        unique_id, uuid = next(result)
        self.assertEqual(res.id, unique_id)
        self.assertEqual('{urn:uuid:%s}' % props.id, uuid)

    def test_search_by_sql_applies_query(self):
        res = self.add_resource('one', type='article')
        self.add_resource('two', type='centerpage')
        query = select(Content).filter_by(type='article')
        result = list(self.connector.search_sql(query))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, res.id)

    def test_search_by_sql_prefills_cache(self):
        self.add_resource('one', body=b'mybody', type='article')
        query = select(Content).filter_by(type='article')
        result = list(self.connector.search_sql(query))
        with mock.patch.object(
            self.connector.session, 'execute', side_effect=RuntimeError('disabled')
        ):
            self.assertEqual(result[0].data.read(), b'mybody')

    def test_search_by_sql_includes_lock_in_cache(self):
        res = self.add_resource('one', body=b'mybody', type='article')
        until = pendulum.now('UTC').add(minutes=5)
        self.connector.lock(res.id, 'someone', until)
        transaction.commit()  # empty cache
        query = select(Content).filter_by(type='article')
        list(self.connector.search_sql(query))
        self.assertNotEqual((None, None, False), self.connector.locked(res.id))

    def test_search_by_sql_reuses_existing_cache(self):
        prop = ('foo', f'{NS}testing')
        res = self.get_resource('foo', b'mybody', {('foo', f'{NS}testing'): 'foo'}, type='article')
        self.connector.add(res)
        self.connector.property_cache[res.id][prop] = 'bar'
        query = select(Content).filter_by(type='article')
        result = list(self.connector.search_sql(query))
        self.assertEqual('bar', result[0].properties[prop])

    def test_search_sql_count_returns_result_count(self):
        self.add_resource('one', type='article')
        self.add_resource('two', type='centerpage')
        self.add_resource('three', type='article')
        query = select(Content).where(sql("type='article'"))
        self.assertEqual(self.connector.search_sql_count(query), 2)

    def test_search_sql_suppresses_errors(self):
        self.connector.session.execute(sql('set local statement_timeout=1'))
        query = select(Content).add_columns(sql('pg_sleep(1)'))
        result = list(self.connector.search_sql(query))
        self.assertEqual(len(result), 0)
        # Ensure no InFailedSqlTransaction exception happens on subsequent calls
        result = list(self.connector.search_sql(select(Content)))
        self.assertEqual(len(result), 1)

    def test_search_sql_count_suppresses_errors(self):
        self.connector.session.execute(sql('set local statement_timeout=1'))
        query = select(Content)
        with mock.patch('sqlalchemy.func.count') as count:
            count.return_value = sql('count(*), pg_sleep(1)')
            self.assertEqual(0, self.connector.search_sql_count(query))
        # Ensure no InFailedSqlTransaction exception happens on subsequent calls
        self.assertEqual(1, self.connector.search_sql_count(query))

    def test_search_sql_supports_separate_timeout(self):
        query = select(Content).add_columns(sql('pg_sleep(1)'))
        assert self.connector.execute_sql(query, timeout=1)

    def test_search_returns_uuid(self):
        res = self.get_resource(
            'foo',
            b'mybody',
            {
                ('foo', f'{NS}testing'): 'foo',
            },
        )
        self.connector.add(res)
        props = self.connector._get_content(res.id)
        UUID = SearchVar('uuid', f'{NS}document')
        FOO = SearchVar('foo', f'{NS}testing')
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
        self.connector.lock(res.id, 'external', pendulum.now('UTC').add(hours=2))
        transaction.commit()
        with self.assertNothingRaised():
            del self.connector['http://xml.zeit.de/testing/folder']

    def _create_lock(self, minutes):
        res = self.get_resource(f'foo-{minutes}', b'mybody')
        self.connector.add(res)
        until = pendulum.now('UTC').add(minutes=minutes)
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
        now = pendulum.now('UTC')
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

    def setUp(self):
        super().setUp()
        Content.date_created.info['migration'] = 'test'

    def tearDown(self):
        Content.date_created.info.pop('migration', None)
        super().tearDown()

    def test_properties_are_written_simultaneously_to_separate_column_and_unsorted(self):
        FEATURE_TOGGLES.set('column_write_test')
        FEATURE_TOGGLES.set('column_read_test')
        timestamp = pendulum.datetime(1980, 1, 1)
        isoformat = timestamp.isoformat()
        res = self.add_resource('foo', properties={('date_created', f'{NS}document'): isoformat})
        self.assertEqual(isoformat, res.properties[('date_created', f'{NS}document')])
        content = self.connector._get_content(res.id)
        self.assertEqual({'document': {'date_created': isoformat}}, content.unsorted)
        self.assertEqual(timestamp, content.date_created)

    def test_properties_can_be_stored_in_separate_columns(self):
        FEATURE_TOGGLES.set('column_write_test')
        FEATURE_TOGGLES.set('column_read_test')
        FEATURE_TOGGLES.set('column_strict_test')
        timestamp = pendulum.datetime(1980, 1, 1)
        isoformat = timestamp.isoformat()
        res = self.add_resource('foo', properties={('date_created', f'{NS}document'): isoformat})
        self.assertEqual(isoformat, res.properties[('date_created', f'{NS}document')])
        content = self.connector._get_content(res.id)
        self.assertEqual({}, content.unsorted)
        self.assertEqual(timestamp, content.date_created)

    def test_search_looks_in_columns_or_unsorted_depending_on_toggle(self):
        FEATURE_TOGGLES.set('column_write_test')

        res = self.add_resource('foo', properties={('ressort', f'{NS}document'): 'Wissen'})
        var = SearchVar('ressort', f'{NS}document')
        for toggle in [False, True]:  # XXX parametrize would be nice
            FEATURE_TOGGLES.factory.override(toggle, 'column_read_test')
            if toggle:
                self.connector._get_content(res.id).unsorted = {}
                transaction.commit()
            result = self.connector.search([var], var == 'Wissen')
            unique_id, uuid = next(result)
            self.assertEqual(res.id, unique_id)

    def test_revoke_write_toggle_must_not_break_checkin(self):
        FEATURE_TOGGLES.set('column_write_test')
        self.repository['testcontent'] = ExampleContentType()
        example_date = pendulum.datetime(2024, 10, 1)
        with checked_out(self.repository['testcontent']) as co:
            IModified(co).date_created = example_date
            FEATURE_TOGGLES.unset('column_write_test')

    def test_delete_property_from_column(self):
        FEATURE_TOGGLES.set('column_write_test')
        FEATURE_TOGGLES.set('column_read_test')
        id = 'http://xml.zeit.de/testcontent'
        self.repository['testcontent'] = ExampleContentType()
        example_date = pendulum.datetime(2024, 1, 1).isoformat()
        prop = ('date_created', 'http://namespaces.zeit.de/CMS/document')
        self.connector.changeProperties(id, {prop: example_date})
        transaction.commit()
        self.connector.changeProperties(id, {prop: DeleteProperty})
        transaction.commit()
        res = self.connector[id]
        self.assertNotIn(prop, res.properties)

    def test_unsorted_properties_must_be_strings(self):
        date = pendulum.datetime(2024, 1, 1)
        with raises(ValueError):
            self.add_resource('foo', properties={('date_created', f'{NS}document'): date})
        FEATURE_TOGGLES.set('column_write_document_date_created')
        with raises(ValueError):
            self.add_resource('bar', properties={('date_created', f'{NS}document'): date})

    def test_convert_exception_includes_column_name(self):
        FEATURE_TOGGLES.set('column_write_test')
        FEATURE_TOGGLES.set('column_read_test')
        with raises(ValueError) as e:
            self.add_resource('foo', properties={('date_created', f'{NS}document'): 'not a date'})
        self.assertIn("Cannot convert 'not a date' to date_created", str(e.value))

    def test_convert_supports_nullable_date_columns(self):
        FEATURE_TOGGLES.set('column_write_test')
        FEATURE_TOGGLES.set('column_read_test')
        res = self.add_resource('foo', properties={('date_created', f'{NS}document'): ''})
        content = self.connector._get_content(res.id)
        self.assertIsNone(content.date_created)

    def test_convert_channels(self):
        res = self.add_resource(
            'foo', properties={('channels', f'{NS}document'): 'main1 sub1;main2'}
        )
        content = self.connector._get_content(res.id)
        self.assertEqual((('main1', 'sub1'), ('main2', None)), content.channels)

    def test_convert_recipe_fields(self):
        res = self.add_resource(
            'foo',
            properties={
                ('categories', f'{NS}recipe'): 'c1;c2',
                ('ingredients', f'{NS}recipe'): 'i1;i2',
                ('titles', f'{NS}recipe'): 't1;t2',
            },
        )
        content = self.connector._get_content(res.id)
        self.assertEqual(('c1', 'c2'), content.recipe_categories)
        self.assertEqual(('i1', 'i2'), content.recipe_ingredients)
        self.assertEqual(('t1', 't2'), content.recipe_titles)


class ColumnDeclarationTest(zeit.connector.testing.TestCase):
    layer = zeit.connector.testing.COLUMNS_ZOPE_LAYER

    def test_column_declarations_match_dav_properties(self):
        declared = {
            (ns.replace(Content.NS, ''), name)
            for name, ns in zeit.cms.content.dav.PROPERTY_REGISTRY.keys()
        }
        for column in Content._columns_with_name('always'):
            ns = column.info['namespace']
            name = column.info['name']
            self.assertIn((ns, name), declared)
