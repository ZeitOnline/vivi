import zeit.content.volume.testing
import zeit.content.volume.interfaces


class TestProductSource(zeit.content.volume.testing.FunctionalTestCase):
    def test_source_is_filtered_by_volume_attribute(self):
        source = zeit.content.volume.interfaces.PRODUCT_SOURCE
        values = list(source(None))
        self.assertEqual(2, len(values))
        self.assertEqual('Die Zeit', values[0].title)
