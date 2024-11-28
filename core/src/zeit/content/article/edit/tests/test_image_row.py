import lxml.builder

from zeit.cms.content.reference import ReferenceProperty
from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.article.edit.image_parallax_properties import ImageParallaxProperties
from zeit.content.article.edit.image_row import ImageRow
import zeit.content.article.testing
import zeit.edit.interfaces


class ImageRowTest(zeit.content.article.testing.FunctionalTestCase):
    def get_image_row(self):
        image_row = ImageRow(None, lxml.builder.E.image_row())
        return image_row

    def test_image_row_should_be_set(self):
        ExampleContentType.images = ReferenceProperty('.body.image', 'image')
        image_row = self.get_image_row()
        image_row.display_mode = 'square'
        image_row.variant_name = 'default'
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        ref.title = 'localtitle'
        ref.caption = 'localcaption'
        image_row.images = (ref,)
        self.assertEqual('square', image_row.xml.xpath('.')[0].get('display_mode'))
        self.assertEqual('default', image_row.xml.xpath('.')[0].get('variant_name'))
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG', image_row.xml.xpath('./image')[0].get('src')
        )

    def test_image_parallax_properties_should_be_set(self):
        image_properties = ImageParallaxProperties(None, lxml.builder.E.image_parallax_properties())

        image_properties.show_source = True
        image_properties.show_caption = True
        self.assertEqual('True', image_properties.xml.xpath('.')[0].get('show_source'))
        self.assertEqual('True', image_properties.xml.xpath('.')[0].get('show_caption'))
