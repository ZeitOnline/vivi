from datetime import datetime
from io import BytesIO
from zeit.connector.resource import Resource, WriteableCachedResource
from zeit.connector.search import SearchVar
import google.api_core.exceptions
import transaction
import zeit.connector.testing


class SQLConnectorTest(zeit.connector.testing.SQLTest):

    def test_serializes_properties_as_json(self):
        res = self.get_resource('foo', b'mybody', {
            ('uuid', 'http://namespaces.zeit.de/CMS/document'):
            '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}',
            ('foo', 'http://namespaces.zeit.de/CMS/one'): 'foo',
            ('bar', 'http://namespaces.zeit.de/CMS/two'): 'bar',
        })
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        self.assertEqual('foo', props.path.name)
        self.assertEqual('/testing', props.path.parent_path)
        self.assertEqual('testing', props.type)
        self.assertEqual(False, props.is_collection)
        self.assertEqual('deadbeaf-c5aa-4232-837a-ae6701270436', props.id)
        self.assertEqual({
            'document': {
                'uuid': '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}'},
            'one': {'foo': 'foo'},
            'two': {'bar': 'bar'},
        }, props.unsorted)

    def test_stores_body_in_gcs_for_configured_binary_content_types(self):
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        blob = self.connector.bucket.blob(props.id)
        self.assertEqual(b'mybody', blob.download_as_bytes())

    def test_injects_uuid_and_type_into_dav_properties(self):
        res = self.get_resource('foo', b'mybody', {
            ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
        })
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        davprops = props.to_webdav()
        self.assertEqual({
            ('uuid', 'http://namespaces.zeit.de/CMS/document'):
            '{urn:uuid:%s}' % props.id,
            ('type', 'http://namespaces.zeit.de/CMS/meta'): 'testing',
            ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
        }, davprops)

    def test_provides_last_updated_column(self):
        # Properly we would test that the value of the last_updated column
        # increases on INSERT and UPDATE. But our test setup wraps everything
        # in an outer transaction, which causes any SQL `NOW()` calls to return
        # the start time of that transaction -- so we cannot detect an increase
        res = self.get_resource('foo')
        self.connector.add(res)
        transaction.commit()
        props = self.connector._get_properties(res.id)
        self.assertIsInstance(props.last_updated, datetime)

    def test_determines_size_for_gcs_upload(self):
        body = b'mybody'
        for res in [
                Resource(
                    'http://xml.zeit.de/testing/foo', 'foo', 'file',
                    BytesIO(body), {}, 'text/plain'),
                WriteableCachedResource(
                    'http://xml.zeit.de/testing/foo', 'foo', 'file',
                    lambda: {}, lambda: BytesIO(body), 'text/plain')]:
            self.connector.add(res)
            props = self.connector._get_properties(res.id)
            blob = self.connector.bucket.blob(props.id)
            self.assertEqual(body, blob.download_as_bytes())

    def test_delete_removes_gcs_blob(self):
        res = self.get_resource('foo', b'mybody')
        res.type = 'file'
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        blob = self.connector.bucket.blob(props.id)
        del self.connector[res.id]
        with self.assertRaises(google.api_core.exceptions.NotFound):
            blob.download_as_bytes()

    def test_delete_removes_rows_from_all_tables(self):
        from zeit.connector.postgresql import Paths, Properties
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        uuid = props.id
        del self.connector[res.id]
        transaction.commit()
        self.assertEqual(
            None,
            self.connector.session.get(Paths, self.connector._pathkey(res.id)))
        self.assertEqual(None, self.connector.session.get(Properties, uuid))

    def test_search_for_uuid_uses_indexed_column(self):
        res = self.get_resource('foo', b'mybody')
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        UUID = SearchVar('uuid', 'http://namespaces.zeit.de/CMS/document')
        result = self.connector.search([UUID], UUID == props.id)
        unique_id, uuid = next(result)
        self.assertEqual(res.id, unique_id)
        self.assertEqual(props.id, uuid)
