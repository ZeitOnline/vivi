from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.content.reference import ReferenceProperty
from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.image.interfaces import IImageMetadata
import zeit.content.image.interfaces
import zeit.content.image.testing
import zope.copypastemove.interfaces


class ImageAssetTest(zeit.content.image.testing.FunctionalTestCase):

    def test_IImages_accepts_IImage_for_backwards_compatibility(self):
        with self.assertNothingRaised():
            zeit.content.image.interfaces.IImages['image'].validate(
                ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG'))


class ImageReferenceTest(zeit.content.image.testing.FunctionalTestCase):

    def setUp(self):
        super(ImageReferenceTest, self).setUp()
        ExampleContentType.images = ReferenceProperty('.body.image', 'image')

    def tearDown(self):
        del ExampleContentType.images
        super(ImageReferenceTest, self).tearDown()

    def test_local_values_override_original_ones(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        ref.title = 'localtitle'
        ref.caption = 'localcaption'
        self.assertEqual('localtitle', ref.title)
        self.assertEqual('localcaption', ref.caption)
        ref.update_metadata()
        self.assertEqual('localtitle', ref.title)
        self.assertEqual('localcaption', ref.caption)

    def test_not_overridable_values_are_always_proxied_to_target(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image) as co:
            IImageMetadata(co).origin = 'originalorigin'
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        self.assertEqual('originalorigin', ref.origin)
        ref.update_metadata()
        self.assertEqual('originalorigin', ref.origin)
        with checked_out(ref.target) as co:
            IImageMetadata(co).origin = 'updatedorigin'
        ref.update_metadata()
        self.assertEqual('updatedorigin', ref.origin)

    def test_empty_local_values_leave_original_ones_alone(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image) as co:
            IImageMetadata(co).title = 'originaltitle'
            IImageMetadata(co).caption = 'originalcaption'
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        self.assertEqual('originaltitle', ref.title)
        self.assertEqual('originalcaption', ref.caption)
        ref.update_metadata()
        self.assertEqual('originaltitle', ref.title)
        self.assertEqual('originalcaption', ref.caption)

    def test_setting_local_value_none_yields_none(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        ref.title = 'localtitle'
        ref.caption = 'localcaption'
        self.assertEqual('localtitle', ref.title)
        self.assertEqual('localcaption', ref.caption)
        ref.title = None
        ref.caption = ''  # the caption field is non-None
        self.assertEqual(None, ref.title)
        self.assertEqual('', ref.caption)

    def test_updater_suppress_errors(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = ICheckoutManager(self.repository['testcontent']).checkout()
        zeit.content.image.interfaces.IImages(content).image = image

        # This error condition cannot be synthesized easily (would need to make
        # an ImageGroup lose its metadata so it's treated as a Folder), and
        # even mocking it is rather complicated, sigh.
        def mock_query(*args, **kw):
            if kw.get('name') == 'image':
                return None
            return queryAdapter(*args, **kw)
        queryAdapter = zope.component.queryAdapter

        with mock.patch('zope.component.queryAdapter', mock_query):
            with self.assertNothingRaised():
                updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                    content)
                updater.update(content.xml, suppress_errors=True)

    def test_colorpicker_should_generate_proper_xml(self):
        content = self.repository['testcontent']
        zeit.content.image.interfaces.IImages(content).fill_color = 'F00F00'
        assert len(content.xml.xpath(
            '//head/image[@fill_color="F00F00"]')) == 1


class MoveReferencesTest(zeit.content.image.testing.FunctionalTestCase):

    def test_moving_image_updates_uniqueId_in_referencing_obj(self):
        # This is basically the same test as zeit.cms.redirect.tests.test_move,
        # but for image references instead of related references.
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(self.repository['testcontent']) as co:
            zeit.content.image.interfaces.IImages(co).image = image

        zope.copypastemove.interfaces.IObjectMover(image).moveTo(
            self.repository, 'changed')

        content = self.repository['testcontent']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                'http://xml.zeit.de/changed',
                zeit.content.image.interfaces.IImages(content).image.uniqueId)
            self.assertFalse(lookup().find.called)
        self.assertIn(
            'http://xml.zeit.de/changed',
            zeit.cms.testing.xmltotext(content.xml))
