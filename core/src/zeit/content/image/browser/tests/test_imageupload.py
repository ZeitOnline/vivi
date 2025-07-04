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

    def test_imagegroup_is_automatically_renameble(self):
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
