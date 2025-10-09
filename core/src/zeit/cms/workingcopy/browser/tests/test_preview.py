import zeit.cms.config
import zeit.cms.testing


class WorkingcopyPreviewTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_redirects_to_preview(self):
        zeit.cms.config.set('zeit.cms', 'preview-prefix', 'http://friedbert/')
        b = self.browser
        b.open('/repository/testcontent/@@checkout')
        b.follow_redirects = False
        link = b.getLink('Preview')
        link.click()
        self.assertEqual(
            'http://friedbert/wcpreview/zope.user/testcontent', b.headers.get('Location')
        )

        b.open(link.url + '?foo=bar')
        self.assertEqual(
            'http://friedbert/wcpreview/zope.user/testcontent?foo=bar', b.headers.get('Location')
        )
