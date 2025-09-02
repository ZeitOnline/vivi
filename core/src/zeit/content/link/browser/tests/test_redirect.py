from zeit.cms.checkout.helper import checked_out
from zeit.content.image.interfaces import IImages
from zeit.content.image.testing import create_image_group
import zeit.content.link.testing


class LinkRedirectTest(zeit.content.link.testing.BrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_copies_metadata_fields(self):
        self.repository['image'] = create_image_group()
        with checked_out(self.repository['testcontent']) as co:
            co.title = 'My Title'
            co.ressort = 'Deutschland'
            co.sub_ressort = 'Integration'
            co.channels = [('Wirtschaft', None)]
            IImages(co).image = self.repository['image']
        b = self.browser
        b.open('/repository/testcontent/@@redirect-box')
        b.getControl('Redirect path').value = '/link'
        b.getControl('Create redirect').click()
        self.assertEllipsis(
            '...<span class="nextURL">http://localhost/++skin++vivi/repository/link...',
            b.contents,
        )
        link = self.repository['link']
        self.assertEqual('My Title', link.title)
        self.assertEqual('http://localhost/live-prefix/testcontent', link.url)
        self.assertEqual(self.repository['image'], IImages(link).image)

        self.assertEqual('Administratives', link.ressort)
        self.assertEqual(None, link.sub_ressort)
        self.assertEqual((), link.channels)
