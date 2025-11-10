import json
import re
import unittest
import urllib

from selenium.webdriver.common.keys import Keys
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.image.browser.imageupload import ImageNameProvider
from zeit.content.image.testing import (
    add_file_multi,
    fixture_bytes,
)
import zeit.cms.browser.interfaces
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.content.image.testing


class ImageUploadBrowserTest(zeit.content.image.testing.BrowserTestCase):
    def test_content_can_access_images_upload_form(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        # The "context views/actions" menu is hidden for this view
        self.assertNotEllipsis('...Checkout...', b.contents)

    def test_redirects_after_upload(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert b.url.endswith(f'/testcontent/@@edit-images?files={img.__name__}')

    def test_does_not_redirect_if_files_field_is_not_in_request(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        with self.assertRaises(urllib.error.HTTPError):
            b.getForm(name='imageupload').submit()
            self.assertEndsWith('/testcontent/@@upload-images', b.url)
            self.assertIn('Please upload at least one image', b.contents)

    def test_does_not_redirect_if_no_image_present(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        with self.assertRaises(urllib.error.HTTPError):
            # We have to hand-craft our POST request, because
            # Testbrowser does not support submitting an empty form field
            b.post(b.getForm(name='imageupload').action, 'files=')
            self.assertEndsWith('/testcontent/@@upload-images', b.url)
            self.assertIn('Please upload at least one image', b.contents)

    def test_redirects_after_upload_in_folder(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert b.url.endswith(f'/@@edit-images?files={img.__name__}')

    def test_can_upload_image(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_rejects_unsupported_mime_types(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [(fixture_bytes('berlin-polizei.webp'), 'foo.webp', 'image/webp')],
        )
        with self.assertRaises(urllib.error.HTTPError):
            b.getForm(name='imageupload').submit()

    def test_can_upload_image_from_folder(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_can_upload_multiple_images(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert len(images) == 2
        for img in images:
            assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_redirects_after_multi_upload(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId)
        # We don't know the exact order of the url params
        assert '/testcontent/@@edit-images?files=' in b.url
        assert re.search('[&?]files=' + re.escape(images[0].__name__) + '(&|$)', b.url)
        assert re.search('[&?]files=' + re.escape(images[1].__name__) + '(&|$)', b.url)

    def test_huge_image_is_resized(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('shoppingmeile_2251x4001px.jpg'),
                    'shoppingmeile_2251x4001px.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        self.assertEqual((2250, 4000), img[img.master_image].getImageSize())

    def test_imagegroup_is_automatically_renameable(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        self.assertTrue(zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).renameable)
        self.assertFalse(zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).rename_to)
        b.getForm(name='edit-images').submit()
        assert not zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).renameable

    def test_upload_sets_timestamps(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        group = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert zeit.content.image.interfaces.IImageGroup.providedBy(group)
        self.assertTrue(zeit.cms.content.interfaces.ISemanticChange(group).last_semantic_change)
        self.assertTrue(zeit.cms.workflow.interfaces.IModified(group).date_created)
        img = group[group.master_image]
        self.assertTrue(zeit.cms.content.interfaces.ISemanticChange(img).last_semantic_change)
        self.assertTrue(zeit.cms.workflow.interfaces.IModified(img).date_created)

    def test_editimages_correctly_names_single_image(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'testcontent-bild'

    def test_editimages_redirects_to_single_image(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getForm(name='edit-images').submit()
        self.assertEndsWith('/repository/testcontent-bild/@@variant.html', b.url)

    def test_editimages_correctly_names_single_image_for_content_that_clashes_with_existing_image(
        self,
    ):
        self.repository['testcontent-bild'] = zeit.content.image.imagegroup.ImageGroup()
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'testcontent-bild-2'

    def test_editimages_correctly_names_single_image_that_clashes_with_existing_image(self):
        self.repository['cycling-bel-renewi-bild'] = zeit.content.image.imagegroup.ImageGroup()
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('gettyimages-2168232879-150x100.jpg'),
                    'gettyimages-2168232879-150x100.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'cycling-bel-renewi-bild-2'

    def test_editimages_correctly_shows_xmp_data(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('gettyimages-2168232879-150x100.jpg'),
                    'gettyimages-2168232879-150x100.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'cycling-bel-renewi-bild'
        assert b.getControl(name='copyright[0]').value == 'DAVID PINTENS/Belga/AFP via Getty Images'
        assert (
            b.getControl(name='caption[0]').value
            == "UAE Team Emirates' German rider Nils Politt competes during stage two of the "
            + '"Renewi Tour" multi-stage cycling race'
        )
        assert b.getControl(name='title[0]').value == 'CYCLING-BEL-RENEWI'

    def test_editimages_correctly_names_image_without_xmp(self):
        group = zeit.content.image.imagegroup.ImageGroup()
        group.master_images = (
            (
                'desktop',
                'master-image.jpg',
            ),
        )
        self.repository['group'] = group
        self.repository['group']['master-image.jpg'] = zeit.content.image.testing.create_image(
            'obama-clinton-120x120.jpg'
        )
        b = self.browser
        b.open('/repository/@@edit-images?files=group')
        assert b.getControl(name='target_name[0]').value == 'master-image-bild'

    def test_editimages_correctly_names_image_without_xmp_after_image_with_xmp(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('gettyimages-2168232879-150x100.jpg'),
                    'gettyimages-2168232879-150x100.jpg',
                    'image/jpg',
                ),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'cycling-bel-renewi-bild'
        assert b.getControl(name='target_name[1]').value == 'opernball-bild'

    def test_editimages_correctly_names_multiple_images_with_same_xmp(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('gettyimages-2168232879-150x100.jpg'),
                    'gettyimages-2168232879-150x100.jpg',
                    'image/jpg',
                ),
                (
                    fixture_bytes('gettyimages-2168232879-150x100.jpg'),
                    'gettyimages-2168232879-150x100.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'cycling-bel-renewi-bild-1'
        assert b.getControl(name='target_name[1]').value == 'cycling-bel-renewi-bild-2'

    def test_editimages_correctly_names_multiple_images(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'testcontent-bild-1'
        assert b.getControl(name='target_name[1]').value == 'testcontent-bild-2'

    def test_editimages_correctly_names_many_images(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        assert b.getControl(name='target_name[0]').value == 'testcontent-bild-01'
        assert b.getControl(name='target_name[1]').value == 'testcontent-bild-02'
        assert b.getControl(name='target_name[9]').value == 'testcontent-bild-10'

    def test_empty_file_name_raises_error(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        self.assertTrue('required' in b.getControl(name='target_name[0]')._elem.attrs)

    def test_editimages_shows_error_on_used_file_name(self):
        self.repository['testcontent-bild'] = zeit.content.image.imagegroup.ImageGroup()
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getControl(name='target_name[0]').value = 'testcontent-bild'
        b.getForm(name='edit-images').submit()
        self.assertEqual(b.getControl(name='target_name[0]').value, 'testcontent-bild')
        self.assertEllipsis(
            '...<span class="error">File name is already in use</span>...', b.contents
        )

    def test_editimages_shows_error_on_duplicate_file_name(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')

        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getControl(name='target_name[0]').value = 'testcontent-bild'
        b.getControl(name='target_name[1]').value = 'testcontent-bild'
        b.getForm(name='edit-images').submit()
        self.assertEqual(b.getControl(name='target_name[0]').value, 'testcontent-bild')
        self.assertEqual(b.getControl(name='target_name[1]').value, 'testcontent-bild')
        self.assertEllipsis(
            '...<span class="error">File name is already in use</span>...', b.contents
        )

    def test_editimages_deletes_files_on_cancel(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getForm(name='edit-images').getControl(name='cancel').click()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId or '-bild' in x.uniqueId)
        assert len(images) == 0
        assert b.url.endswith('/repository/testcontent/')

    def test_editimages_normalizes_user_input_file_name(self):
        b = self.browser
        b.open('/repository/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getControl(name='target_name[0]').value = 'this is not normal(ized)'
        b.getForm(name='edit-images').submit()
        assert zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/this-is-not-normal-ized')

    def test_publish_images_after_upload(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getForm(name='edit-images').getControl(name='upload_and_publish').click()

        self.assertTrue(IPublishInfo(self.repository['testcontent-bild-1']).published)
        self.assertTrue(IPublishInfo(self.repository['testcontent-bild-2']).published)

    def test_open_single_image_after_upload(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getForm(name='edit-images')
        b.getControl(name='target_name[0]').value == 'testcontent-bild'
        b.getForm(name='edit-images').getControl(name='upload_and_open').click()

        self.assertEndsWith('/repository/testcontent-bild/@@variant.html', b.url)

    def test_open_multiple_images_after_upload(self):
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (fixture_bytes('opernball.jpg'), 'opernball.jpg', 'image/jpg'),
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                ),
            ],
        )
        b.getForm(name='imageupload').submit()
        b.getControl(name='target_name[0]').value = 'testcontent-bild-1'
        b.getControl(name='target_name[1]').value = 'testcontent-bild-2'
        b.getForm(name='edit-images').getControl(name='upload_and_open').click()
        self.assertEllipsis(
            '...http://localhost/++skin++vivi/repository/testcontent-bild-2/@@variant.html...'
            'http://localhost/++skin++vivi/repository/testcontent-bild-1/@@variant.html...',
            b.contents,
        )

    def test_upload_image_has_properties(self):
        FEATURE_TOGGLES.set('column_read_wcm_56')
        FEATURE_TOGGLES.set('column_write_wcm_56')
        FEATURE_TOGGLES.set('calculate_accent_color')
        b = self.browser
        b.open('/repository/testcontent/@@upload-images')
        file_input = b.getControl(name='files')
        add_file_multi(
            file_input,
            [
                (
                    fixture_bytes('new-hampshire-450x200.jpg'),
                    'new-hampshire-450x200.jpg',
                    'image/jpg',
                )
            ],
        )
        b.getForm(name='imageupload').submit()
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        master_img = zeit.content.image.interfaces.IMasterImage(img)
        self.assertEqual(450, master_img.width)
        self.assertEqual(200, master_img.height)
        self.assertEqual(master_img._mime_type, master_img.mimeType)
        self.assertEqual('202310', master_img.accent_color)


class ImageUploadSeleniumTest(zeit.content.image.testing.SeleniumTestCase):
    def _fake_drop(self, drop_target, data):
        self.execute(
            """const event = document.createEvent("CustomEvent");
            event.initCustomEvent("drop", true, true, null);
            event.dataTransfer = new DataTransfer();
            event.dataTransfer.setData("text/plain", """
            + json.dumps(data)
            + """);
            document.querySelector("""
            + json.dumps(drop_target)
            + """).dispatchEvent(event);"""
        )

    def test_drop_mdb_image(self):
        zope.component.getGlobalSiteManager().registerUtility(zeit.content.image.mdb.FakeMDB())
        self.open('/repository/@@upload-images')
        self._fake_drop(
            '.imageupload__drop',
            json.dumps(
                {
                    'module': 'mdb',
                    'data': [41733454],
                    'thumb_map': {
                        '41733454': '/mdb_data/147/2025/09/10/4/1/7/3/3/MDB41733454TN_25c72dd5c1.IR'
                        + 'ZEITPROD_NQGJA.jpg'
                    },
                    'preview_thumb_map': {
                        '41733454': '/mdb_data/147/2025/09/10/4/1/7/3/3/PMDB41733454TN_25c72dd5c1.I'
                        + 'RZEITPROD_NQGJA.jpg'
                    },
                    'href_map': {
                        '41733454': '/exec/ir_engine.pl?sid=bdbc2171a90b3ae0a3ccc6c21b4a32e7&linkf'
                        + 'ile=image.IRZEITPROD_NQGJA.jpg&file=/mdb_data/147/2025/09/10/4/1/7/3/3/'
                        + 'MDB41733454_25c72dd5c1.IRZEITPROD_NQGJA.jpg'
                    },
                }
            ),
        )
        self.selenium.waitForElementPresent('css=.imageupload__gallery li')
        self.selenium.assertText('css=.imageupload__gallery .imageupload__filename', 'image.jpg')
        self.selenium.click('css=.imageupload__button--submit')
        self.selenium.waitForLocation('*/repository/@@edit-images?files=*')

    def test_enter_mdb_id(self):
        s = self.selenium
        zope.component.getGlobalSiteManager().registerUtility(zeit.content.image.mdb.FakeMDB())
        self.open('/repository/@@upload-images')
        s.type('css=.imageupload__mdb-ids', '12345')
        s.keyPress('css=.imageupload__mdb-ids', Keys.RETURN)
        s.waitForElementPresent('css=.imageupload__gallery li')
        s.assertText(
            'css=.imageupload__gallery .imageupload__filename',
            'MDB2752_4ed1cf12e4.IRZEITDEV_14L.jpg',  # FIXME: We don't get the nice name yet
        )
        s.assertValue('css=.imageupload__mdb-ids', '')
        s.click('css=.imageupload__button--submit')
        s.waitForLocation('*/repository/@@edit-images?files=*')
        self.selenium.assertValue('name=target_name[0]', 'mdb-bild-titel-bild')
        self.selenium.assertValue('name=copyright[0]', 'mdb-copyright-foo/Peter Schwalbach')
        self.selenium.assertValue('name=title[0]', 'mdb-bild-titel')
        self.selenium.assertValue('name=caption[0]', 'Testbilder Honorar')


class AddCentralImageUploadTest(zeit.content.image.testing.SeleniumTestCase):
    def test_new_image_upload_is_present(self):
        s = self.selenium
        self.open('/')

        s.waitForElementPresent('sidebar.form.type_')

        # successful submit
        s.select('sidebar.form.type_', 'Image (new)')
        s.click('name=sidebar.form.actions.add')
        s.waitForLocation('*/@@upload-images?')


class AddMenuImageUploadTest(zeit.content.image.testing.BrowserTestCase):
    def test_new_image_upload_is_present(self):
        b = self.browser
        b.open('/repository')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (new)']
        b.open(menu.value[0])
        assert 'http://localhost/++skin++vivi/repository/@@upload-images' == b.url


class ImageNameProviderTest(unittest.TestCase):
    def test_correctly_names_only_image(self):
        provider = ImageNameProvider({})
        name = provider.get('base-name')
        self.assertEqual(str(name), 'base-name-bild')

    def test_correctly_names_two_images(self):
        provider = ImageNameProvider({})
        name1 = provider.get('base-name')
        name2 = provider.get('base-name')
        self.assertEqual(str(name1), 'base-name-bild-1')
        self.assertEqual(str(name2), 'base-name-bild-2')

    def test_correctly_names_eleven_images(self):
        provider = ImageNameProvider({})
        names = tuple(
            (provider.get('base-name'), suffix)
            for suffix in ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11')
        )
        for name, suffix in names:
            self.assertEqual(str(name), 'base-name-bild-' + suffix)

    def test_correctly_names_image_with_one_in_context(self):
        provider = ImageNameProvider({'base-name-bild': None})
        name = provider.get('base-name')
        self.assertEqual(str(name), 'base-name-bild-2')

    def test_correctly_names_image_with_two_in_context(self):
        provider = ImageNameProvider({'base-name-bild-1': None, 'base-name-bild-2': None})
        name = provider.get('base-name')
        self.assertEqual(str(name), 'base-name-bild-3')

    def test_correctly_names_image_with_eleven_in_context(self):
        provider = ImageNameProvider(
            {
                'base-name-bild-01': None,
                'base-name-bild-02': None,
                'base-name-bild-03': None,
                'base-name-bild-04': None,
                'base-name-bild-05': None,
                'base-name-bild-06': None,
                'base-name-bild-07': None,
                'base-name-bild-08': None,
                'base-name-bild-09': None,
                'base-name-bild-10': None,
                'base-name-bild-11': None,
            }
        )
        name = provider.get('base-name')
        self.assertEqual(str(name), 'base-name-bild-12')
