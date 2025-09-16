import transaction
import zope.component

from zeit.cms.content.interfaces import IXMLReference
from zeit.cms.interfaces import ICMSContent
from zeit.content.image.interfaces import IImageMetadata
import zeit.content.image.metadata
import zeit.content.image.testing


class ImageMetadataTest(zeit.content.image.testing.FunctionalTestCase):
    def set_copyright(self, value):
        image = ICMSContent('http://xml.zeit.de/image')
        with zeit.cms.checkout.helper.checked_out(image) as co:
            metadata = IImageMetadata(co)
            metadata.copyright = value
        return image

    def test_nofollow_is_written_to_rel_attribute(self):
        image = self.set_copyright((('Foo', 'http://example.com', True),))
        ref = zope.component.getAdapter(image, IXMLReference, name='image')
        self.assertEllipsis(
            """\
<image src="http://xml.zeit.de/image" type="jpeg"/>
""",
            zeit.cms.testing.xmltotext(ref),
        )

    def test_related_reference_to_image_does_not_overwrite_href(self):
        image = ICMSContent('http://xml.zeit.de/group')
        node = zope.component.getAdapter(
            image, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual(image.uniqueId, node.get('href'))

    def test_related_reference_to_imagegroup_does_not_overwrite_href(self):
        group = self.repository['group']
        image = group['master-image.jpg']
        node = zope.component.getAdapter(
            image, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual(image.uniqueId, node.get('href'))

    def test_bw_compat_copyright(self):
        # Tuple of pairs
        image = self.set_copyright((('foo', 'bar'),))
        self.assertEqual(('foo', None, None, 'bar', False), IImageMetadata(image).copyright)
        transaction.commit()
        # Tuple of triples
        image = self.set_copyright((('foo', 'bar', True),))
        self.assertEqual(('foo', None, None, 'bar', True), IImageMetadata(image).copyright)
        transaction.commit()
        # Tuple of quintuples
        image = self.set_copyright((('foo', 'bar', 'baz', 'qux', True),))
        self.assertEqual(('foo', 'bar', 'baz', 'qux', True), IImageMetadata(image).copyright)
