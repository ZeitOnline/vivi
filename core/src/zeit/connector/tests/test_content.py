from zeit.cms.checkout.helper import checked_out
import zeit.cms.testing
import zeit.connector.testing


class MetadataColumnTest(zeit.cms.testing.FunctionalTestCase):
    # layer = zeit.connector.testing.CONTENT_LAYER
    layer = zeit.cms.testing.ZOPE_LAYER

    def setUp(self):
        super().setUp()
        zeit.cms.config.set('zeit.connector', 'connector_read_metadata_columns', True)
        zeit.cms.config.set('zeit.connector', 'connector_write_metadata_columns', True)

    def test_uses_sql_datatype_on_read(self):
        self.repository.connector.changeProperties(
            'http://xml.zeit.de/testcontent',
            {('overscrolling', 'http://namespaces.zeit.de/CMS/document'): True},
        )
        self.assertIs(True, self.repository['testcontent'].overscrolling)

    def test_uses_sql_datatype_on_write(self):
        with checked_out(self.repository['testcontent']) as co:
            co.overscrolling = True
        resource = self.repository.connector['http://xml.zeit.de/testcontent']
        self.assertIs(
            True, resource.properties[('overscrolling', 'http://namespaces.zeit.de/CMS/document')]
        )
