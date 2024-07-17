# coding: utf-8
from unittest import mock

from zope.publisher.interfaces import NotFound
import PIL
import zope.event
import zope.lifecycleevent

from zeit.cms.workflow.interfaces import IPublicationDependencies
from zeit.content.image import imagegroup
from zeit.content.image.testing import create_image_group_with_master_image, create_local_image
import zeit.cms.repository.interfaces
import zeit.content.image.testing


class ImageGroupTest(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group = create_image_group_with_master_image()
        self.request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer
        )
        self.full_traverser = zope.component.getMultiAdapter(
            (self.group, self.request), zope.publisher.interfaces.IPublishTraverse
        )
        self.traverser = zeit.content.image.imagegroup.VariantTraverser(self.group, self.request)

    def traverse(self, name):
        return self.full_traverser.publishTraverse(self.request, name)

    def test_getitem_returns_dav_content(self):
        image = self.traverse('master-image.jpg')
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))

    def test_getitem_creates_image_from_variant_if_no_dav_content(self):
        image = self.traverse('square')
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertEqual(self.group, image.__parent__)
        self.assertEqual('square', image.__name__)
        self.assertEqual('http://xml.zeit.de/group/square', image.uniqueId)

    def test_getitem_raises_keyerror_for_unmapped_legacy_names(self):
        with self.assertRaises(NotFound):
            self.traverse('master-image-111x222.jpg')

    def test_getitem_raises_keyerror_for_wrongly_mapped_legacy_names(self):
        with self.assertRaises(NotFound):
            self.traverse('master-image-148x84.jpg')

    def test_getitem_handles_viewport_modifier(self):
        with self.assertNothingRaised():
            self.traverse('square__mobile')

    def test_getitem_defines_no_variant_source_for_materialized_files(self):
        """It raises AttributeError when asked for `variant_source`.

        Since `variant_source` is used for testing only, we do not want to add
        it to `BaseImage`. Thus only variants created using
        `ImageGroupBase.create_variant_image` should have this attribute.

        """
        image = self.traverse('master-image.jpg')
        with self.assertRaises(AttributeError):
            image.variant_source

    def test_getitem_uses_primary_master_image_if_no_viewport_was_given(self):
        image = self.traverse('square')
        self.assertEqual('master-image.jpg', image.variant_source)

    def test_getitem_uses_primary_master_image_if_viewport_not_configured(self):
        """Default configuration only includes `desktop`, but not `mobile`."""
        image = self.traverse('square__mobile')
        self.assertEqual('master-image.jpg', image.variant_source)

    def test_getitem_chooses_master_image_using_given_viewport(self):
        """Uses master-image for desktop and master-image-mobile for mobile."""
        self.group['master-image-mobile.jpg'] = create_local_image('obama-clinton-120x120.jpg')
        with mock.patch(
            'zeit.content.image.imagegroup.ImageGroupBase.master_images',
            new_callable=mock.PropertyMock,
        ) as master_images:
            master_images.return_value = (
                ('desktop', 'master-image.jpg'),
                ('mobile', 'master-image-mobile.jpg'),
            )
            self.assertEqual('master-image.jpg', self.traverse('square__desktop').variant_source)
            self.assertEqual(
                'master-image-mobile.jpg', self.traverse('square__mobile').variant_source
            )

    def test_getitem_ignores_master_image_for_viewport_if_nonexistent(self):
        with mock.patch(
            'zeit.content.image.imagegroup.ImageGroupBase.master_images',
            new_callable=mock.PropertyMock,
        ) as master_images:
            master_images.return_value = (('desktop', 'nonexistent.jpg'),)
            self.assertEqual('master-image.jpg', self.traverse('square__desktop').variant_source)

    def test_getitem_raises_keyerror_if_variant_does_not_exist(self):
        with self.assertRaises(NotFound):
            self.traverse('nonexistent')

    def test_variant_url_returns_path_with_size_if_given(self):
        self.assertEqual('/group/square__200x200', self.group.variant_url('square', 200, 200))

    def test_variant_url_returns_path_without_size_if_none_given(self):
        self.assertEqual('/group/square', self.group.variant_url('square'))

    def test_variant_url_handles_non_ascii(self):
        group = self.repository['groüp'] = self.group
        self.assertEqual('/groüp/square', group.variant_url('square'))

    def test_returns_image_for_variant_with_size(self):
        self.assertEqual((200, 200), self.traverse('square__200x200').getImageSize())

    def test_invalid_size_raises_keyerror(self):
        with self.assertRaises(NotFound):
            self.traverse('square__0x200')

        with self.assertRaises(NotFound):
            self.traverse('square__-1x200')

    def test_variant_url_returns_path_with_fill_color_if_given(self):
        self.assertEqual(
            '/group/square__200x200__0000ff', self.group.variant_url('square', 200, 200, '0000ff')
        )

        self.assertEqual(
            '/group/square__300x300', self.group.variant_url('square', 300, 300, 'None')
        )

        self.assertEqual('/group/square__400x400', self.group.variant_url('square', 400, 400, None))

    def test_dav_content_with_same_name_is_preferred(self):
        self.assertEqual((1536, 1536), self.traverse('square').getImageSize())
        self.group['square'] = zeit.content.image.testing.create_local_image(
            'new-hampshire-450x200.jpg'
        )
        self.assertEqual((450, 200), self.traverse('square').getImageSize())

    def test_thumbnails_create_variants_from_smaller_master_image(self):
        self.assertEqual((1536, 1536), self.traverse('square').getImageSize())
        thumbnails = zeit.content.image.interfaces.IThumbnails(self.group)
        self.assertEqual((750, 750), thumbnails['square'].getImageSize())

    def test_can_access_small_variant_via_name_and_size(self):
        variant = self.traverser._parse_variant_by_size('cinema__200x100')
        self.assertEqual('cinema-small', variant.id)

    def test_defaults_to_variant_without_size_limitation_if_size_too_big(self):
        variant = self.traverser._parse_variant_by_size('cinema__9999x9999')
        self.assertEqual('cinema-large', variant.id)

    def test_invalid_names_should_return_none(self):
        self.assertEqual(None, self.traverser._parse_variant_by_size('foobarbaz__9999x9999'))
        self.assertEqual(None, self.traverser._parse_variant_by_size('cinema__200xfoo'))
        self.assertEqual(None, self.traverser._parse_variant_by_size('cinema__800x'))

    def test_no_size_matches_returns_none(self):
        from zeit.content.image.variant import Variant, Variants

        with mock.patch.object(
            Variants, 'values', return_value=[Variant(name='foo', id='small', max_size='100x100')]
        ):
            self.assertEqual(None, self.traverser._parse_variant_by_size('foo__9999x9999'))

    def test_master_image_is_None_if_no_master_images_defined(self):
        group = zeit.content.image.imagegroup.ImageGroup()
        self.assertEqual(None, group.master_image)

    def test_master_image_retrieves_first_image_from_master_images(self):
        group = zeit.content.image.imagegroup.ImageGroup()
        group.master_images = (('viewport', 'master.png'),)
        self.assertEqual('master.png', group.master_image)

    def test_master_image_is_retrieved_from_DAV_properties_for_bw_compat(self):
        from zeit.content.image.interfaces import IMAGE_NAMESPACE

        group = zeit.content.image.imagegroup.ImageGroup()
        properties = zeit.connector.interfaces.IWebDAVReadProperties(group)
        properties[('master_image', IMAGE_NAMESPACE)] = 'master.png'
        self.assertEqual('master.png', group.master_image)

    def test_master_image_for_viewport_ignores_if_nonexistent(self):
        with mock.patch(
            'zeit.content.image.imagegroup.ImageGroupBase.master_images',
            new_callable=mock.PropertyMock,
        ) as master_images:
            master_images.return_value = (('desktop', 'nonexistent.jpg'),)
            self.assertEqual(
                'master-image.jpg', self.group.master_image_for_viewport('desktop').__name__
            )

    def test_device_pixel_ratio_affects_image_size(self):
        self.assertEqual((600, 320), self.traverse('cinema__300x160__scale_2.0').getImageSize())
        self.assertEqual((180, 96), self.traverse('cinema__300x160__scale_0.6').getImageSize())
        self.assertEqual((675, 360), self.traverse('cinema__300x160__scale_2.25').getImageSize())

    def test_unallowed_device_pixel_ratio_is_ignored(self):
        self.assertEqual((300, 160), self.traverse('cinema__300x160__scale_0.2').getImageSize())
        self.assertEqual((300, 160), self.traverse('cinema__300x160__scale_99999').getImageSize())

    def test_scaled_image_get_zoom_from_non_scaled_size(self):
        self.group.variants = {
            'cinema-small': {'zoom': 0.3, 'max_size': '300x160'},
            'cinema-large': {'zoom': 1.0, 'max_size': '600x320'},
        }
        self.assertEqual(
            0.3, self.traverser._parse_variant_by_size('cinema__300x160__scale_2.0').zoom
        )
        self.assertEqual(0.3, self.traverser._parse_variant_by_size('cinema__300x160').zoom)
        self.assertEqual(1.0, self.traverser._parse_variant_by_size('cinema__600x320').zoom)

    def test_does_not_change_external_id_when_already_set(self):
        meta = zeit.content.image.interfaces.IImageMetadata(self.group)
        meta.external_id = '12345'
        self.group['6789.jpg'] = create_local_image('opernball.jpg')
        zope.event.notify(zope.lifecycleevent.ObjectAddedEvent(self.traverse('6789.jpg')))
        self.assertEqual('12345', meta.external_id)

    def test_delete_group_does_not_try_to_recreate_deleted_children(self):
        with self.assertNothingRaised():
            del self.group.__parent__[self.group.__name__]

    def test_create_variant_image_allows_overriding_output_format(self):
        image = self.group.create_variant_image(
            zeit.content.image.interfaces.IVariants(self.group)['square'], format='WEBP'
        )
        self.assertEqual('image/webp', image.mimeType)
        with image.open() as f:
            image = PIL.Image.open(f)
            image.load()
        self.assertEqual('WEBP', image.format)

    def test_create_variant_image_allows_overriding_output_format_avif(self):
        image = self.group.create_variant_image(
            zeit.content.image.interfaces.IVariants(self.group)['square'], format='AVIF'
        )
        self.assertEqual('image/avif', image.mimeType)
        with image.open() as f:
            image = PIL.Image.open(f)
            image.load()
        self.assertEqual('AVIF', image.format)

    def test_parse_url_variant(self):
        result = self.traverser.parse_url('cinema__300x160__scale_2.25__0000ff')
        assert result['variant'].name == 'cinema'
        assert result['size'] == [300, 160]
        assert result['scale'] == 2.25
        assert result['fill'] == '0000ff'
        assert result['viewport'] is None

    def test_parse_url_variant_params(self):
        result = self.traverser.parse_url(
            'cinema__200x80__scale_2.25__0000ff?scale=3.0&width=300&height=160&fill=000000'
        )
        assert result['size'] == [300, 160]
        assert result['scale'] == 3.0
        assert result['fill'] == '000000'
        assert result['viewport'] is None

    def test_parse_fill_None_should_return_NoneType(self):
        result = self.traverser.parse_url(
            'cinema__200x80__scale_2.25__0000ff?scale=3.0&width=300&height=160&fill=None'
        )
        assert result['size'] == [300, 160]
        assert result['scale'] == 3.0
        assert result['fill'] is None
        assert result['viewport'] is None

    def test_parse_url_variant_params_only(self):
        result = self.traverser.parse_url(
            '?variant=cinema&scale=3.0&width=300&height=160&fill=000000'
        )
        assert result['variant'].name == 'cinema'
        assert result['size'] == [300, 160]
        assert result['scale'] == 3.0
        assert result['fill'] == '000000'
        assert result['viewport'] is None

    def test_parse_url_variant_params_override(self):
        result = self.traverser.parse_url(
            'cinema__200x80__scale_2.25__0000ff?scale=3.0&width=300&height=160&fill=000000'
        )
        assert result['size'] == [300, 160]
        assert result['scale'] == 3.0
        assert result['fill'] == '000000'
        assert result['viewport'] is None

    def test_parse_size_from_params(self):
        result = self.traverser.parse_params('cinema?scale=3.0&width=300&height=160')
        assert result['size'] == [300, 160]

    def test_parse_scale_from_params(self):
        result = self.traverser.parse_params('cinema?scale=3.0&width=300&height=160')
        assert result['scale'] == 3.0

    def test_parse_fill_from_params(self):
        result = self.traverser.parse_params('cinema?fill=0000ff&scale=3.0&width=300&height=160')
        assert result['fill'] == '0000ff'

    def test_parse_viewport_from_params(self):
        result = self.traverser.parse_params('cinema?fill=0000ff&viewport=foo')
        assert result['viewport'] == 'foo'


class ImageGroupFromImageTest(zeit.content.image.testing.FunctionalTestCase):
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    def test_image_group_from_image(self):
        repository = self.repository()
        local_image = create_local_image('opernball.jpg')
        group = zeit.content.image.imagegroup.ImageGroup.from_image(
            repository, 'group', local_image
        )
        assert group.master_image == 'opernball.jpg'

    def test_image_group_from_none(self):
        repository = self.repository()
        group = zeit.content.image.imagegroup.ImageGroup.from_image(repository, 'group', None)
        assert group.master_image is None


class ImageGroupFromImage(zeit.content.image.testing.BrowserTestCase):
    def test_image_group_from_image(self):
        local_image = zeit.content.image.testing.create_local_image('opernball.jpg')
        imagegroup.ImageGroup.from_image(self.repository, 'group', local_image)
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository' '/group/@@metadata.html')


class ExternalIDTest(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group = create_image_group_with_master_image()

    def search(self, filename):
        context = mock.Mock()
        context.__parent__ = self.group
        context.__name__ = filename
        zeit.content.image.imagegroup.guess_external_id(context, None)
        meta = zeit.content.image.interfaces.IImageMetadata(self.group)
        result = meta.external_id
        meta.external_id = None
        return result

    def test_external_id_matches_single_number_in_filename(self):
        self.assertEqual(None, self.search('asdf-120x120.jpg'))
        self.assertEqual('90999280', self.search('dpa Picture-Alliance-90999280-HighRes.jpg'))
        self.assertEqual('90997723', self.search('90997723-HighRes Kopie.jpg'))
        self.assertEqual('90997723', self.search('90997723.jpg'))

    def test_external_id_matches_reuters_filenames(self):
        self.assertEqual('rtsu6hm', self.search('rtsu6hm.jpg'))
        self.assertEqual('RTSU6HM', self.search('RTSU6HM.jpg'))
        self.assertEqual('rtsü6hm', self.search('rtsü6hm.jpg'))
        self.assertEqual('6', self.search('Kopie von rtsu6hm.jpg'))
        self.assertEqual(None, self.search('wartsnurab.jpg'))


class ThumbnailsTest(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        from ..imagegroup import Thumbnails

        super().setUp()
        self.group = create_image_group_with_master_image()
        self.thumbnails = Thumbnails(self.group)

    def test_uses_master_image_for_thumbnails(self):
        self.assertEqual(self.group['master-image.jpg'], self.thumbnails.master_image('square'))

    def test_uses_image_defined_for_viewport_desktop_when_given(self):
        self.assertEqual(
            self.group['master-image.jpg'], self.thumbnails.master_image('square__desktop')
        )

    def test_uses_image_defined_for_viewport_mobile_when_given(self):
        self.group['master-image-mobile.jpg'] = create_local_image('obama-clinton-120x120.jpg')
        with mock.patch(
            'zeit.content.image.imagegroup.ImageGroupBase.master_images',
            new_callable=mock.PropertyMock,
        ) as master_images:
            master_images.return_value = (
                ('desktop', 'master-image.jpg'),
                ('mobile', 'master-image-mobile.jpg'),
            )
            self.assertEqual(
                self.group['master-image-mobile.jpg'],
                self.thumbnails.master_image('square__mobile'),
            )

    def test_recreates_thumbnails_on_reload_event(self):
        del self.group['thumbnail-source-master-image.jpg']
        zope.event.notify(zeit.cms.repository.interfaces.ObjectReloadedEvent(self.group))
        self.assertIn('thumbnail-source-master-image.jpg', self.group.keys())

    def test_thumbnail_is_removed_on_delete(self):
        self.group['second'] = create_local_image('new-hampshire-450x200.jpg')
        self.thumbnails.THUMBNAIL_WIDTH = 100
        self.thumbnails.source_image(self.group['second'])
        del self.group['second']
        self.assertEqual(
            ['master-image.jpg', 'thumbnail-source-master-image.jpg'], self.group.keys()
        )

    def test_thumbnail_is_not_published(self):
        dependencies = IPublicationDependencies(self.group).get_dependencies()
        self.assertIn(self.group['master-image.jpg'], dependencies)
        self.assertNotIn(self.thumbnails.source_image(self.group['master-image.jpg']), dependencies)
