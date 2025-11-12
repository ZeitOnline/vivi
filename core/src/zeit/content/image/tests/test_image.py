from unittest import mock
import importlib.resources

import requests_mock
import zope.component
import zope.event
import zope.lifecycleevent

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.content.image.testing import create_image
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.content.image.image
import zeit.content.image.testing


class TestImageMetadataAcquisition(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group = self.repository['group']
        with zeit.cms.checkout.helper.checked_out(self.group) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            metadata.title = 'Title'

    @property
    def img(self):
        return self.group['master-image.jpg']

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

    def test_read_embedded_image_metadata(self):
        image = create_image('gettyimages-2168232879-150x100.jpg')
        metadata = image.embedded_metadata_flattened()
        self.assertEqual(metadata['xmp:xmpmeta:Source'], 'AFP')
        self.assertEqual(metadata['xmp:xmpmeta:Headline'], 'CYCLING-BEL-RENEWI')
        self.assertEqual(metadata['xmp:xmpmeta:creator'], 'DAVID PINTENS')

    def test_flatten(self):
        image = create_image('gettyimages-2168232879-150x100.jpg')
        metadata = image._flatten({'foo': ['bar', {'baz': 0}, 1]})
        self.assertEqual(metadata, {'foo': 1, 'foo:baz': 0})

        metadata = image._flatten({'foo': {'baz': 0}, 'bar': 1})
        self.assertEqual(metadata, {'bar': 1, 'foo:baz': 0})

        metadata = image._flatten({'foo': ['bar', 1, 1.1]})
        self.assertEqual(metadata, {'foo': 'bar, 1, 1.1'})

    def test_flatten_raises_silently(self):
        image = create_image('gettyimages-2168232879-150x100.jpg')
        with mock.patch('zeit.content.image.image.BaseImage._flatten', side_effect=Exception):
            self.assertEqual(image.embedded_metadata_flattened(), {})


class TestImageXMLReference(zeit.content.image.testing.FunctionalTestCase):
    def test_master_image_without_filename_extension_sets_mime_as_type(self):
        ref = zope.component.getAdapter(
            self.repository['image'],
            zeit.cms.content.interfaces.IXMLReference,
            name='image',
        )
        self.assertEqual('jpeg', ref.get('type'))


class TestImageMIMEType(zeit.content.image.testing.FunctionalTestCase):
    def test_ignores_stored_dav_mime_type(self):
        with checked_out(self.repository['image']) as co:
            props = zeit.connector.interfaces.IWebDAVProperties(co)
            props[('getcontenttype', 'DAV:')] = 'image/png'
        self.assertEqual('image/jpeg', self.repository['image'].mimeType)


class TestImageProperties(zeit.content.image.testing.FunctionalTestCase):
    def test_create_image_sets_properties(self):
        FEATURE_TOGGLES.set('calculate_accent_color')
        image = zeit.content.image.testing.create_image()
        self.repository['image-with-properties'] = image
        image = self.repository['image-with-properties']
        self.assertEqual('image/jpeg', image.mimeType)
        self.assertEqual(119, image.width)
        self.assertEqual(160, image.height)
        self.assertEqual('8f7223', image.accent_color)

    def test_create_image_from_remote_sets_properties(self):
        FEATURE_TOGGLES.set('calculate_accent_color')

        def callback(*args):
            image = (
                importlib.resources.files('zeit.connector') / 'testcontent/2006' / 'DSC00109_2.JPG'
            )
            with open(image, 'rb') as fd:
                image_bytes = fd.read()
            return image_bytes

        rmock = requests_mock.Mocker()
        rmock.register_uri('GET', 'https://example.test/image', content=callback)
        with rmock:
            image = zeit.content.image.image.get_remote_image('https://example.test/image')
        self.repository['image-with-properties'] = image
        image = self.repository['image-with-properties']
        self.assertEqual('image/jpeg', image.mimeType)
        self.assertEqual(2048, image.width)
        self.assertEqual(1536, image.height)
        self.assertEqual('28818b', image.accent_color)

    def test_update_image_updates_properties(self):
        FEATURE_TOGGLES.set('calculate_accent_color')
        self.repository['image-with-properties'] = zeit.content.image.testing.create_image()
        image = self.repository['image-with-properties']
        self.assertEqual('image/jpeg', image.mimeType)
        self.assertEqual(119, image.width)
        self.assertEqual(160, image.height)
        with checked_out(image) as co:
            file = (
                importlib.resources.files('zeit.connector') / 'testcontent/2006' / 'DSC00109_2.JPG'
            )
            with open(file, 'rb') as data:
                with co.open('w') as f:
                    f.write(data.read())
        image = self.repository['image-with-properties']
        self.assertEqual('image/jpeg', image.mimeType)
        self.assertEqual(2048, image.width)
        self.assertEqual(1536, image.height)
        self.assertEqual('8f7223', image.accent_color)

    def test_copy_image_does_not_violate_security(self):
        new_name = 'new-image'
        self.repository['image-with-properties'] = zeit.content.image.testing.create_image()
        obj = self.repository['image-with-properties']

        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        new = repository.getCopyOf(obj.uniqueId)
        del new.__parent__
        del new.__name__
        self.repository[new_name] = new
        new = self.repository[new_name]
        # would fail with zope.security.interfaces.Forbidden, because the object is not checked out
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(new, obj))
        self.assertEqual(self.repository[new_name].mimeType, obj.mimeType)
