from zeit.cms.checkout.helper import checked_out
from zeit.content.image.interfaces import IImages
import zeit.content.link.testing


class LinkRedirectTest(zeit.content.link.testing.BrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_copies_metadata_fields(self):
        image = self.repository['2006']['DSC00109_2.JPG']
        with checked_out(self.repository['testcontent']) as co:
            co.title = 'My Title'
            IImages(co).image = image
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/' '@@redirect-box')
        b.getControl('Redirect path').value = '/link'
        b.getControl('Create redirect').click()
        self.assertEllipsis(
            '...<span class="nextURL">http://localhost/++skin++vivi/repository' '/link...',
            b.contents,
        )
        link = self.repository['link']
        self.assertEqual('My Title', link.title)
        self.assertEqual('http://localhost/live-prefix/testcontent', link.url)
        self.assertEqual(image, IImages(link).image)
