import zope.component

import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.content.image.interfaces
import zeit.content.image.testing


class ImageDetails(zeit.content.image.testing.SeleniumTestCase):
    def test_clicking_button_shows_details_pane(self):
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        repository['image-with-metadata'] = zeit.content.image.testing.create_local_image(
            'gettyimages-2168232879-150x100.jpg'
        )
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/image-with-metadata')
        with zeit.cms.checkout.helper.checked_out(image) as co:
            meta = zeit.content.image.interfaces.IImageMetadata(co)
            meta.caption = 'foo'

        s = self.selenium
        self.open('/repository/image-with-metadata/@@wrap?view=object-details')
        s.assertNotVisible('css=.picture_information')
        self.execute('window.jQuery(document).trigger_fragment_ready();')
        s.click('css=.toggle_infos')
        s.waitForVisible('css=.picture_information')


class ImageDetailsErrorHandling(zeit.content.image.testing.BrowserTestCase):
    def test_no_image_exists_still_renders(self):
        self.repository['group'] = zeit.content.image.imagegroup.ImageGroup()
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/group/@@object-details-body')
        self.assertEllipsis('...edit-button...', b.contents)

    def test_metadata_view(self):
        self.repository['group'] = zeit.content.image.imagegroup.ImageGroup()
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/group/@@metadata.html')
