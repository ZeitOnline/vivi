from zeit.cms.interfaces import ICMSContent
from zeit.cms.repository.folder import Folder
from zeit.cms.repository.interfaces import IFolder
from zeit.content.gallery.gallery import Gallery
from zeit.content.image.testing import add_file_multi, fixture_bytes
import zeit.content.gallery.testing


class GalleryUI(zeit.content.gallery.testing.BrowserTestCase):
    def test_redirects_to_synchronize_after_upload(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['folder'] = Folder()
            gallery = Gallery()
            gallery.image_folder = self.repository['folder']
            self.repository['gallery'] = gallery

        b = self.browser
        b.open('/repository/gallery/@@checkout')
        b.getLink('Upload Images').click()
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
        b.getForm(name='edit-images').submit()

        self.assertEqual(
            'http://localhost/++skin++vivi/workingcopy/zope.user/gallery/@@overview.html', b.url
        )
        self.assertEllipsis(
            '...<img src="http://localhost/++skin++vivi/repository/folder/thumbnails/gallery-bild/@@raw"...',
            b.contents,
        )

    def test_creates_image_folder_if_none_given(self):
        b = self.browser
        b.open('/repository')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Gallery']
        b.open(menu.value[0])

        b.getControl('File name').value = 'island'
        b.getControl('Title').value = 'Auf den Spuren der Elfen'
        b.getControl('Ressort', index=0).displayValue = ['Reisen']
        b.getControl(name='form.actions.add').click()
        self.assertNotEllipsis('...There were errors...', b.contents)

        folder = ICMSContent('http://xml.zeit.de/island-bilder')
        self.assertTrue(IFolder.providedBy(folder))
        gallery = ICMSContent('http://xml.zeit.de/island')
        self.assertEqual(folder, gallery.image_folder)
