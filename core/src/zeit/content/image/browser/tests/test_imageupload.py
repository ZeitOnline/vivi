import re

import webtest.forms

from zeit.content.image.testing import fixture_bytes
import zeit.cms.browser.interfaces
import zeit.cms.interfaces
import zeit.content.image.testing


# zope.testbrowser.browser.Control.add_file cannot yet handle multiple file inputs as implemented by
# https://github.com/Pylons/webtest/commit/d1dbc25f53a031d03112cb1e44f4a060cf3665cd
def add_file_multi(control, files):
    control._form[control.name] = [
        webtest.forms.Upload(filename, file, content_type)
        for (file, filename, content_type) in files
    ]


class ImageUploadBrowserTest(zeit.content.image.testing.BrowserTestCase):
    def test_article_has_images_upload_form(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
        # The "context views/actions" menu is hidden for this view
        self.assertNotEllipsis('...Checkout...', b.contents)

    def test_redirects_after_upload(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert b.url.endswith(f'/2007/01/@@edit-images?files={img.__name__}&from=Somalia')

    def test_does_not_redirect_if_files_field_is_not_in_request(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
        b.getForm(name='imageupload').submit()
        self.assertEndsWith('/2007/01/Somalia/@@upload-images', b.url)
        self.assertIn('Please upload at least one image', b.contents)
        self.assertEqual('200 Ok', b.headers['status'])

    def test_does_not_redirect_if_no_image_present(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
        # We have to hand-craft our POST request, because
        # Testbrowser does not support submitting an empty form field
        b.post(b.getForm(name='imageupload').action, 'files=')
        self.assertEndsWith('/2007/01/Somalia/@@upload-images', b.url)
        self.assertIn('Please upload at least one image', b.contents)
        self.assertEqual('200 Ok', b.headers['status'])

    def test_redirects_after_upload_in_folder(self):
        b = self.browser
        b.open('/repository/online/2007/01/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert b.url.endswith(f'/2007/01/@@edit-images?files={img.__name__}')

    def test_can_upload_image(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_can_upload_image_from_folder(self):
        b = self.browser
        b.open('/repository/online/2007/01/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_can_upload_multiple_images(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId)
        assert len(images) == 2
        for img in images:
            assert zeit.content.image.interfaces.IImageGroup.providedBy(img)

    def test_redirects_after_multi_upload(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId)
        # We don't know the exact order of the url params
        assert '/2007/01/@@edit-images?files=' in b.url
        assert re.search('[&?]files=' + re.escape(images[0].__name__) + '(&|$)', b.url)
        assert re.search('[&?]files=' + re.escape(images[1].__name__) + '(&|$)', b.url)
        assert re.search('[&?]from=Somalia(&|$)', b.url)

    def test_huge_image_is_resized(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        self.assertEqual((2250, 4000), img[img.master_image].getImageSize())

    def test_imagegroup_is_automatically_renameable(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        img = next(x for x in folder.values() if 'tmp' in x.uniqueId)
        self.assertTrue(zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).renameable)
        self.assertFalse(zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).rename_to)
        b.getForm(name='edit-images').submit()
        assert not zeit.cms.repository.interfaces.IAutomaticallyRenameable(img).renameable

    def test_editimages_correctly_names_single_image(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        assert b.getControl(name='name[0]').value == 'Somalia-bild'

    def test_editimages_redirects_to_single_image(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        self.assertEndsWith('/repository/online/2007/01/Somalia-bild/@@variant.html', b.url)

    def test_editimages_correctly_names_single_image_for_article_that_clashes_with_existing_image(
        self,
    ):
        self.repository['online']['2007']['01']['Somalia-bild'] = (
            zeit.content.image.imagegroup.ImageGroup()
        )
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        assert b.getControl(name='name[0]').value == 'Somalia-bild-2'

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
        assert b.getControl(name='name[0]').value == 'cycling-bel-renewi-bild-2'

    def test_editimages_correctly_shows_xmp_data(self):
        b = self.browser
        b.open('/repository/online/2007/01/@@upload-images')
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
        assert b.getControl(name='name[0]').value == 'cycling-bel-renewi-bild'
        assert b.getControl(name='copyright[0]').value == 'DAVID PINTENS/Belga/AFP via Getty Images'
        assert (
            b.getControl(name='caption[0]').value
            == "UAE Team Emirates' German rider Nils Politt competes during stage two of the "
            + '"Renewi Tour" multi-stage cycling race'
        )
        assert b.getControl(name='title[0]').value == 'CYCLING-BEL-RENEWI'

    def test_editimages_correctly_names_image_without_xmp(self):
        b = self.browser
        b.open('/repository/2007/03/@@edit-images?files=group')
        assert b.getControl(name='name[0]').value == ''

    def test_editimages_correctly_names_multiple_images(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        assert b.getControl(name='name[0]').value == 'Somalia-bild-1'
        assert b.getControl(name='name[1]').value == 'Somalia-bild-2'

    def test_editimages_correctly_names_many_images(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        assert b.getControl(name='name[0]').value == 'Somalia-bild-01'
        assert b.getControl(name='name[1]').value == 'Somalia-bild-02'
        assert b.getControl(name='name[9]').value == 'Somalia-bild-10'

    def test_editimages_can_handle_non_renaming(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        filename = b.getControl(name='cur_name[0]').value
        b.getControl(name='name[0]').value = filename
        b.getForm(name='edit-images').submit()
        assert zeit.cms.interfaces.ICMSContent(f'http://xml.zeit.de/online/2007/01/{filename}')

    def test_empty_file_name_raises_error(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        self.assertTrue('required' in b.getControl(name='name[0]')._elem.attrs)

    def test_editimages_deletes_files_on_cancel(self):
        b = self.browser
        b.open('/repository/online/2007/01/Somalia/@@upload-images')
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
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01')
        images = tuple(x for x in folder.values() if 'tmp' in x.uniqueId or '-bild' in x.uniqueId)
        assert len(images) == 0
        assert b.url.endswith('/repository/online/2007/01/')


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
        b.open('http://localhost:8080/++skin++vivi/repository/online/2007/01/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (new)']
        b.open(menu.value[0])
        assert (
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/@@upload-images' == b.url
        )
