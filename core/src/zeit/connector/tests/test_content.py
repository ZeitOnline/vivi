from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testing
import zeit.connector.testing


class MetadataColumnTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.connector.testing.CONTENT_LAYER

    def setUp(self):
        super().setUp()
        zeit.cms.config.set('zeit.connector', 'connector_read_metadata_columns', True)
        zeit.cms.config.set('zeit.connector', 'connector_write_metadata_columns', True)

    def test_uses_sql_datatype(self):
        self.repository['testcontent'] = ExampleContentType()
        self.repository.connector.changeProperties(
            'http://xml.zeit.de/testcontent',
            {('overscrolling', 'http://namespaces.zeit.de/CMS/document'): True},
        )
        self.assertIs(True, self.repository['testcontent'].overscrolling)
