from datetime import datetime
import transaction
import zeit.connector.testing


class SQLConnectorTest(zeit.connector.testing.SQLTest):

    def test_serialization(self):
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
        self.assertEqual(b'mybody', props.body.body)
        self.assertEqual({
            'document': {'uuid': '{urn:uuid:deadbeaf-c5aa-4232-837a-ae6701270436}'},
            'one': {'foo': 'foo'},
            'two': {'bar': 'bar'},
        }, props.unsorted)

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
