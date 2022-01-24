import zeit.connector.testing


class SQLConnectorTest(zeit.connector.testing.SQLTest):

    def test_serialization(self):
        res = self.get_resource('foo', b'mybody', {
            ('uuid', 'http://namespaces.zeit.de/CMS/document'):
            '{urn:uuid:myid}',
            ('foo', 'http://namespaces.zeit.de/CMS/one'): 'foo',
            ('bar', 'http://namespaces.zeit.de/CMS/two'): 'bar',
        })
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        self.assertEqual('/testing/foo', props.url)
        self.assertEqual('/testing', props.parent_url)
        self.assertEqual('testing', props.type)
        self.assertEqual(False, props.is_collection)
        self.assertEqual('myid', props.id)
        self.assertEqual(b'mybody', props.body.body)
        self.assertEqual({
            'document': {'uuid': '{urn:uuid:myid}'},
            'one': {'foo': 'foo'},
            'two': {'bar': 'bar'},
        }, props.unsorted)

    def test_injects_uuid_and_type_into_dav_properties(self):
        res = self.get_resource('foo', b'mybody', {
            ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
        })
        self.connector.add(res)
        props = self.connector._get_properties(res.id)
        davprops = props.to_dict()
        self.assertEqual({
            ('uuid', 'http://namespaces.zeit.de/CMS/document'):
            '{urn:uuid:%s}' % props.id,
            ('type', 'http://namespaces.zeit.de/CMS/meta'): 'testing',
            ('foo', 'http://namespaces.zeit.de/CMS/testing'): 'foo',
        }, davprops)
