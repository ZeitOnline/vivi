from zeit.cms.content.interfaces import IXMLReference
from zeit.cms.interfaces import ICMSContent
from zeit.content.image.interfaces import IImageMetadata
import lxml.etree
import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.image.metadata
import zope.component


class ImageMetadataTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def set_copyrights(self, value):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with zeit.cms.checkout.helper.checked_out(image) as co:
            metadata = IImageMetadata(co)
            metadata.copyrights = value
        return image

    def test_nofollow_is_written_to_rel_attribute(self):
        image = self.set_copyrights((('Foo', 'http://example.com', True),))
        ref = zope.component.getAdapter(image, IXMLReference, name='image')
        self.assertEllipsis("""\
<image...>
  ...
  <copyright py:pytype="str" link="http://example.com"
        rel="nofollow">Foo</copyright>
</image>
""", lxml.etree.tostring(ref, pretty_print=True))

    def test_related_reference_to_image_does_not_overwrite_href(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        node = zope.component.getAdapter(
            image, zeit.cms.content.interfaces.IXMLReference,
            name='related')
        self.assertEqual(image.uniqueId, node.get('href'))

    def test_related_reference_to_imagegroup_does_not_overwrite_href(self):
        group = zeit.content.image.testing.create_image_group()
        image = group['new-hampshire-450x200.jpg']
        node = zope.component.getAdapter(
            image, zeit.cms.content.interfaces.IXMLReference,
            name='related')
        self.assertEqual(image.uniqueId, node.get('href'))

    def test_bw_compat_copyrights(self):
        # Tuple of pairs
        image = self.set_copyrights((('foo', 'bar'),))
        self.assertEqual(
            ('foo', None, None, 'bar', False),
            IImageMetadata(image).copyrights
        )
        # Tuple of triples
        image = self.set_copyrights((('foo', 'bar', True),))
        self.assertEqual(
            ('foo', None, None, 'bar', True),
            IImageMetadata(image).copyrights
        )
        # Tuple of quintuples
        image = self.set_copyrights((('foo', 'bar', 'baz', 'qux', True),))
        self.assertEqual(
            ('foo', 'bar', 'baz', 'qux', True),
            IImageMetadata(image).copyrights
        )
