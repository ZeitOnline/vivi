import lxml.builder

from zeit.content.article.edit.image_parallax_properties import ImageParallaxProperties
from zeit.content.article.edit.image_row import ImageRow
import zeit.content.article.testing
import zeit.edit.interfaces


class ImageRowTest(zeit.content.article.testing.FunctionalTestCase):
    def get_image_row(self):
        image_row = ImageRow(None, lxml.builder.E.image_row())
        return image_row

    def test_image_row_should_be_set(self):
        from zeit.content.image.testing import create_image_group_with_master_image

        # (<zeit.content.image.imagegroup.ImageGroup http://xml.zeit.de/2024-11/hund>, None, None)
        image_row = self.get_image_row()
        image_row.display_mode = 'square'
        image_row.variant_name = 'default'
        image_group = create_image_group_with_master_image()
        image_row.images = (
            (
                image_group,
                'Fortune of Count Olaf',
                'fortune-count-olaf',
            ),
        )
        self.assertEqual('square', image_row.xml.xpath('.')[0].get('display_mode'))
        self.assertEqual('default', image_row.xml.xpath('.')[0].get('variant_name'))
        self.assertEqual(
            'http://xml.zeit.de/group/', image_row.xml.xpath('./image')[0].get('base-id')
        )
        self.assertEqual('Fortune of Count Olaf', image_row.xml.xpath('./image')[0].get('caption'))
        self.assertEqual('fortune-count-olaf', image_row.xml.xpath('./image')[0].get('alt_text'))

    def test_image_parallax_properties_should_be_set(self):
        image_properties = ImageParallaxProperties(None, lxml.builder.E.image_parallax_properties())

        image_properties.show_source = True
        image_properties.show_caption = True
        self.assertEqual('True', image_properties.xml.xpath('.')[0].get('show_source'))
        self.assertEqual('True', image_properties.xml.xpath('.')[0].get('show_caption'))
