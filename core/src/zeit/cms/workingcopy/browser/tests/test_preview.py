import zeit.cms.config
import zeit.cms.testing


class WorkingcopyPreviewTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_should_not_upload_for_friedbert(self):
        zeit.cms.config.set('zeit.cms', 'preview-prefix', 'http://friedbert/')
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository' '/online/2007/01/Somalia/@@checkout')
        b.follow_redirects = False
        b.getLink('Preview').click()
        url = b.headers.get('Location')
        self.assertEqual('http://friedbert/wcpreview/zope.user/Somalia', url)
