# coding: utf-8
from zeit.content.image.testing import create_image_group_with_master_image
import pkg_resources
import zeit.cms.interfaces
import zeit.content.image.testing


class ImageGroupHelperMixin:

    def add_imagegroup(self, filename='imagegroup', fill_copyright=True):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image group']
        b.open(menu.value[0])

        # Those information are required but rarely used in tests.
        self.set_filename(filename)
        if fill_copyright:
            self.fill_copyright_information()

    def add_motif(self):
        self.browser.getControl('Add motif').click()

    def set_filename(self, filename):
        self.browser.getControl('File name').value = filename

    def set_title(self, title):
        self.browser.getControl('Image title').value = title

    def set_display_type(self, display_type):
        self.browser.getControl('Display Type').displayValue = [display_type]

    def fill_copyright_information(self):
        b = self.browser
        b.getControl(name='form.copyright.combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyright.combination_01').displayValue = (
            ['dpa'])
        b.getControl(name='form.copyright.combination_03').value = (
            'http://www.zeit.de/')

    def _upload_image(self, field, filename):
        if filename.startswith(zeit.cms.interfaces.ID_NAMESPACE):
            self._upload_cms_content(field, uniqueId=filename)
            return
        self.browser.getControl(name='form.{}'.format(field)).add_file(
            pkg_resources.resource_string(
                'zeit.content.image.browser', f'testdata/{filename}'),
            'image/jpeg', filename)

    def _upload_cms_content(self, field, uniqueId):
        file = zeit.cms.interfaces.ICMSContent(uniqueId)
        with file.open() as f:
            self.browser.getControl(name='form.{}'.format(field)).add_file(
                f, 'image/jpeg', uniqueId.split('/')[-1])

    def upload_primary_image(self, filename):
        self._upload_image('master_image_blobs.0.', filename)

    def upload_secondary_image(self, filename):
        self._upload_image('master_image_blobs.1.', filename)

    def upload_tertiary_image(self, filename):
        self._upload_image('master_image_blobs.2.', filename)

    def save_imagegroup(self):
        self.browser.getControl(name='form.actions.add').click()


class ImageGroupGhostTest(
        zeit.content.image.testing.BrowserTestCase,
        ImageGroupHelperMixin):

    def test_adding_imagegroup_adds_a_ghost(self):
        self.add_imagegroup()
        self.set_title('New Hampshire')
        self.upload_primary_image('new-hampshire-artikel.jpg')
        self.save_imagegroup()
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        self.assertEqual(1, len(wc))


class ImageGroupBrowserTest(
        zeit.content.image.testing.BrowserTestCase,
        ImageGroupHelperMixin):

    def test_resize_too_large_images_before_upload_width(self):
        self.add_imagegroup()
        self.upload_primary_image('shoppingmeile_4001x2251px.jpg')
        self.save_imagegroup()
        img = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/imagegroup/shoppingmeile-4001x2251px.jpg')
        assert(img.getImageSize()) == (4000, 2250)

    def test_resize_too_large_images_before_upload_height(self):
        self.add_imagegroup()
        self.upload_primary_image('shoppingmeile_2251x4001px.jpg')
        self.save_imagegroup()
        img = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/imagegroup/shoppingmeile-2251x4001px.jpg')
        assert(img.getImageSize()) == (2250, 4000)

    def test_resize_too_large_secondary_images_before_upload_height(self):
        self.add_imagegroup()
        self.add_motif()
        self.upload_primary_image('opernball.jpg')
        self.upload_secondary_image('shoppingmeile_2251x4001px.jpg')
        self.save_imagegroup()
        img = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/imagegroup/shoppingmeile-2251x4001px.jpg')
        assert(img.getImageSize()) == (2250, 4000)

    def test_traversing_thumbnail_yields_images(self):
        create_image_group_with_master_image()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/group/thumbnails/square/@@raw')
        self.assertEqual('image/jpeg', b.headers['Content-Type'])

    def test_primary_master_image_is_marked_for_desktop_viewport(self):
        self.add_imagegroup()
        self.upload_primary_image('opernball.jpg')
        self.save_imagegroup()

        group = self.repository['imagegroup']
        self.assertEqual(1, len(group.master_images))
        self.assertEqual('desktop', group.master_images[0][0])
        self.assertEqual('opernball.jpg', group.master_images[0][1])

    def test_secondary_master_image_is_marked_for_mobile_viewport(self):
        self.add_imagegroup()
        self.add_motif()
        self.upload_primary_image('opernball.jpg')
        self.upload_secondary_image('new-hampshire-artikel.jpg')
        self.save_imagegroup()

        group = self.repository['imagegroup']
        self.assertEqual(2, len(group.master_images))
        self.assertEqual('mobile', group.master_images[1][0])
        self.assertEqual(
            'new-hampshire-artikel.jpg', group.master_images[1][1])

    def test_tertiary_master_image_has_no_viewport(self):
        self.add_imagegroup()
        self.add_motif()
        self.add_motif()
        self.upload_primary_image('opernball.jpg')
        self.upload_secondary_image('new-hampshire-artikel.jpg')
        self.upload_tertiary_image('obama-clinton-120x120.jpg')
        self.save_imagegroup()
        group = self.repository['imagegroup']
        self.assertEqual(2, len(group.master_images))
        self.assertEqual(3, len(group.keys()))
        self.assertIn('obama-clinton-120x120.jpg', group.keys())

    def test_display_type_imagegroup_uses_variant_html_by_default(self):
        self.add_imagegroup()
        self.set_display_type('Bildergruppe')
        self.save_imagegroup()
        b = self.browser
        self.assertEndsWith('@@variant.html', b.url)
        b.open('http://localhost/++skin++vivi/repository/imagegroup')
        self.assertEndsWith('@@variant.html', b.url)

    def test_display_type_infographic_uses_view_html_by_default(self):
        self.add_imagegroup()
        self.set_display_type('Infografik')
        self.save_imagegroup()
        b = self.browser
        self.assertEndsWith('@@view.html', b.url)
        b.open('http://localhost/++skin++vivi/repository/imagegroup')
        self.assertEndsWith('@@view.html', b.url)

    def test_display_type_imagegroup_shows_edit_tab(self):
        self.add_imagegroup()
        self.set_display_type('Bildergruppe')
        self.save_imagegroup()
        self.assertEllipsis(
            '...repository/imagegroup/@@variant.html...',
            self.browser.contents)

    def test_display_type_infographic_hides_edit_tab(self):
        self.add_imagegroup()
        self.set_display_type('Infografik')
        self.save_imagegroup()
        self.assertNotEllipsis(
            '...repository/imagegroup/@@variant.html...',
            self.browser.contents)

    def test_prefills_external_id_from_image_filename(self):
        b = self.browser
        self.add_imagegroup()
        b.getControl(name='form.master_image_blobs.0.').add_file(
            pkg_resources.resource_string(
                'zeit.content.image.browser',
                'testdata/opernball.jpg'),
            'image/jpeg', 'dpa Picture-Alliance-90999280-HighRes.jpg')
        self.save_imagegroup()
        group = self.repository['imagegroup']
        self.assertEqual(
            '90999280',
            zeit.content.image.interfaces.IImageMetadata(group).external_id)

    def test_normalizes_image_filename_on_upload(self):
        self.add_imagegroup()
        self.browser.getControl(name='form.master_image_blobs.0.').add_file(
            pkg_resources.resource_string(
                'zeit.content.image.browser',
                'testdata/new-hampshire-artikel.jpg'),
            'image/jpeg', 'föö.jpg'.encode('utf-8'))
        self.save_imagegroup()
        group = self.repository['imagegroup']
        self.assertEqual(['foeoe.jpg'], list(group.keys()))

    def test_group_rejects_unsupported_mime_types_on_upload(self):
        self.add_imagegroup()
        self.upload_primary_image('berlin-polizei.webp')
        self.save_imagegroup()
        self.assertEllipsis(
            '...Unsupported image type...', self.browser.contents)


class ImageGroupWebdriverTest(zeit.content.image.testing.SeleniumTestCase):

    def setUp(self):
        super().setUp()
        create_image_group_with_master_image()

    def test_visibility_of_origin_field_depends_on_display_type(self):
        sel = self.selenium
        origin = 'css=.fieldname-origin'
        display_type = r'css=#form\.display_type'
        sel.open('/repository/group/@@checkout')

        sel.select(display_type, 'label=Infografik')
        sel.assertVisible(origin)

        sel.select(display_type, 'label=Bildergruppe')
        sel.assertNotVisible(origin)

    def test_origin_field_is_hidden_in_read_only_mode_if_not_infographic(self):
        sel = self.selenium
        sel.open('/repository/group/@@metadata.html')
        sel.assertNotVisible('css=.fieldname-origin')

    def test_photographer_is_shown_if_company_is_chosen(self):
        sel = self.selenium
        photographer = r'css=#form\.copyright\.combination_00'
        company = r'css=#form\.copyright\.combination_01'
        sel.open('/repository/group/@@checkout')

        sel.assertVisible(photographer)
        sel.select(company, 'label=dpa')
        sel.assertVisible(photographer)

        sel.select(company, 'label=Andere')
        sel.assertNotVisible(photographer)

    def test_freetext_is_only_shown_if_special_company_value_is_selected(self):
        sel = self.selenium
        freetext = r'css=#form\.copyright\.combination_02'
        company = r'css=#form\.copyright\.combination_01'
        sel.open('/repository/group/@@checkout')

        sel.assertNotVisible(freetext)
        sel.select(company, 'label=dpa')
        sel.assertNotVisible(freetext)

        sel.select(company, 'label=Andere')
        sel.assertVisible(freetext)


class ThumbnailTest(zeit.content.image.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.content.image.browser.imagegroup import Thumbnail
        super().setUp()
        self.group = create_image_group_with_master_image()
        self.thumbnail = Thumbnail()
        self.thumbnail.context = self.group

    def test_defaults_to_master_image(self):
        self.assertEqual(
            self.group['master-image.jpg'], self.thumbnail._find_image())

    def test_uses_materialized_image_if_present(self):
        from zeit.content.image.testing import create_local_image
        self.group['image-540x304.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        self.assertEqual(
            self.group['image-540x304.jpg'], self.thumbnail._find_image())


class ThumbnailBrowserTest(
        zeit.content.image.testing.BrowserTestCase,
        ImageGroupHelperMixin):

    def test_thumbnail_source_is_created_on_add(self):
        self.add_imagegroup()
        self.upload_primary_image('http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.save_imagegroup()
        group = self.repository['imagegroup']
        self.assertIn('thumbnail-source-dsc00109-2.jpg', group)

    def test_thumbnail_images_are_hidden_in_content_listing(self):
        self.add_imagegroup()
        self.upload_primary_image('http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.save_imagegroup()
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/imagegroup/view.html')
        self.assertEqual(
            ['dsc00109-2.jpg', 'thumbnail-source-dsc00109-2.jpg'],
            [x.__name__ for x in self.repository['imagegroup'].values()])
        self.assertNotIn('thumbnail-source-DSC00109_2.JPG', b.contents)
