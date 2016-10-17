from zeit.content.image.testing import create_image_group_with_master_image
import gocept.testing.assertion
import mock
import pkg_resources
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.image.testing
import zeit.edit.interfaces
import zeit.edit.rule
import zope.component


class ImageGroupHelperMixin(object):

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
        b.getControl(name='form.copyrights.0..combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyrights.0..combination_01').value = (
            'http://www.zeit.de/')

    def _upload_image(self, field, filename):
        if filename.startswith(zeit.cms.interfaces.ID_NAMESPACE):
            self._upload_cms_content(field, uniqueId=filename)
            return
        self.browser.getControl(name='form.{}'.format(field)).add_file(
            pkg_resources.resource_stream(
                'zeit.content.image.browser',
                'testdata/{}'.format(filename)),
            'image/jpeg', filename)

    def _upload_cms_content(self, field, uniqueId):
        with zeit.cms.testing.site(self.getRootFolder()):
            file = zeit.cms.interfaces.ICMSContent(uniqueId)
        self.browser.getControl(name='form.{}'.format(field)).add_file(
            file.open(), 'image/jpeg', uniqueId.split('/')[-1])

    def upload_primary_image(self, filename):
        self._upload_image('master_image_blobs.0.', filename)

    def upload_secondary_image(self, filename):
        self._upload_image('master_image_blobs.1.', filename)

    def upload_tertiary_image(self, filename):
        self._upload_image('master_image_blobs.2.', filename)

    def save_imagegroup(self):
        self.browser.getControl(name='form.actions.add').click()


class ImageGroupGhostTest(
        zeit.cms.testing.BrowserTestCase,
        ImageGroupHelperMixin):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_adding_imagegroup_adds_a_ghost(self):
        self.add_imagegroup()
        self.set_title('New Hampshire')
        self.upload_primary_image('new-hampshire-artikel.jpg')
        self.save_imagegroup()

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                self.assertEqual(1, len(wc))


class ImageGroupPublishTest(zeit.cms.testing.BrowserTestCase):
    """Integration test for zeit.workflow.browser.publish.Publish.

    Checks that adapter to use ValidatingWorkflow was set up correctly.

    """

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_validation_errors_are_displayed_during_publish(self):
        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        rules = [rm.create_rule(['error_if(True, "Custom Error")'], 0)]
        with mock.patch.object(zeit.edit.rule.RulesManager, 'rules', rules):
            b = self.browser
            b.open('http://localhost/++skin++vivi/repository/2007/03/group'
                   '/@@publish.html')
        self.assertEllipsis('...Custom Error...', b.contents)


class ImageGroupBrowserTest(
        zeit.cms.testing.BrowserTestCase,
        ImageGroupHelperMixin,
        gocept.testing.assertion.String):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_traversing_thumbnail_yields_images(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                create_image_group_with_master_image()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/group/thumbnails/square/@@raw')
        self.assertEqual('image/jpeg', b.headers['Content-Type'])

    def test_primary_master_image_is_marked_for_desktop_viewport(self):
        self.add_imagegroup()
        self.upload_primary_image('opernball.jpg')
        self.save_imagegroup()

        with zeit.cms.testing.site(self.getRootFolder()):
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

        with zeit.cms.testing.site(self.getRootFolder()):
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

        with zeit.cms.testing.site(self.getRootFolder()):
            group = self.repository['imagegroup']
        self.assertEqual(2, len(group.master_images))
        self.assertEqual(3, len(group.keys()))
        self.assertIn('obama-clinton-120x120.jpg', group.keys())

    def test_display_type_imagegroup_opens_variant_html_on_save(self):
        self.add_imagegroup()
        self.set_display_type('Bildergruppe')
        self.save_imagegroup()
        self.assertEndsWith('@@variant.html', self.browser.url)

    def test_display_type_infographic_opens_view_html_on_save(self):
        self.add_imagegroup()
        self.set_display_type('Infografik')
        self.save_imagegroup()
        self.assertEndsWith('@@view.html', self.browser.url)

    def test_display_type_imagegroup_shows_edit_tab(self):
        self.add_imagegroup()
        self.set_display_type('Bildergruppe')
        self.save_imagegroup()
        self.assertIn(
            'repository/imagegroup/@@variant.html', self.browser.contents)

    def test_display_type_infographic_hides_edit_tab(self):
        self.add_imagegroup()
        self.set_display_type('Infografik')
        self.save_imagegroup()
        self.assertNotIn(
            'repository/imagegroup/@@variant.html', self.browser.contents)


class ThumbnailTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        from zeit.content.image.browser.imagegroup import Thumbnail
        super(ThumbnailTest, self).setUp()
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
        zeit.cms.testing.BrowserTestCase,
        ImageGroupHelperMixin):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_thumbnail_source_is_created_on_add(self):
        self.add_imagegroup()
        self.upload_primary_image('http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.save_imagegroup()

        with zeit.cms.testing.site(self.getRootFolder()):
            group = self.repository['imagegroup']
        self.assertIn('thumbnail-source-DSC00109_2.JPG', group)

    def test_thumbnail_images_are_hidden_in_content_listing(self):
        self.add_imagegroup()
        self.upload_primary_image('http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.save_imagegroup()

        b = self.browser
        b.open('http://localhost/++skin++cms/repository/imagegroup/view.html')

        with zeit.cms.testing.site(self.getRootFolder()):
            self.assertEqual(
                ['DSC00109_2.JPG', 'thumbnail-source-DSC00109_2.JPG'],
                [x.__name__ for x in self.repository['imagegroup'].values()])
            self.assertNotIn('thumbnail-source-DSC00109_2.JPG', b.contents)
