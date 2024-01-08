import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.content.image.testing import create_image_group, create_local_image
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.content.image.image
import zeit.content.image.testing


class TestImageMetadataAcquisition(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group_id = create_image_group().uniqueId
        with zeit.cms.checkout.helper.checked_out(self.group) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            metadata.title = 'Title'

    @property
    def group(self):
        return zeit.cms.interfaces.ICMSContent(self.group_id)

    @property
    def img(self):
        return self.group['new-hampshire-450x200.jpg']

    def test_acquired_in_repository(self):
        metadata = zeit.content.image.interfaces.IImageMetadata(self.img)
        self.assertEqual('Title', metadata.title)

    def test_acquired_in_workingcopy(self):
        with zeit.cms.checkout.helper.checked_out(self.img) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            self.assertEqual('Title', metadata.title)
            metadata.title = 'Image title'
        metadata = zeit.content.image.interfaces.IImageMetadata(self.img)
        self.assertEqual('Image title', metadata.title)

    def test_in_workingcopy_when_removed_in_repository(self):
        co = zeit.cms.checkout.interfaces.ICheckoutManager(self.img).checkout()
        del self.group[self.img.__name__]
        metadata = zeit.content.image.interfaces.IImageMetadata(co)
        self.assertEqual(None, metadata.title)


class TestImageXMLReference(zeit.content.image.testing.FunctionalTestCase):
    def test_master_image_without_filename_extension_sets_mime_as_type(self):
        image = zeit.content.image.image.LocalImage()
        with image.open('w') as out:
            with self.repository['2006']['DSC00109_2.JPG'].open() as fh:
                out.write(fh.read())
        self.repository['example-image'] = image
        ref = zope.component.getAdapter(
            self.repository['example-image'],
            zeit.cms.content.interfaces.IXMLReference,
            name='image',
        )
        self.assertEqual('jpeg', ref.get('type'))


class TestImageMIMEType(zeit.content.image.testing.FunctionalTestCase):
    def test_ignores_stored_dav_mime_type(self):
        self.repository['image'] = create_local_image('opernball.jpg')
        with checked_out(self.repository['image']) as co:
            props = zeit.connector.interfaces.IWebDAVProperties(co)
            props[('getcontenttype', 'DAV:')] = 'image/png'
        self.assertEqual('image/jpeg', self.repository['image'].mimeType)
