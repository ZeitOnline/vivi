import zeit.content.volume.testing


class TestProductSource(zeit.content.volume.testing.FunctionalTestCase):

    def test_source_is_filtered_by_volume_attribute(self):
        from zeit.content.volume.interfaces import ProductSource
        source = ProductSource()
        values = list(source(None))
        self.assertEqual(1, len(values))
        self.assertEqual('Die Zeit', values[0].title)
