import urllib2
import zeit.cms.testing
import zope.app.appsetup.product


class WorkingcopyPreviewTest(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def test_should_not_upload_for_friedbert(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        config['preview-prefix'] = 'http://friedbert/'

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.mech_browser.set_handle_redirect(False)
        try:
            b.getLink('Preview').click()
        except urllib2.HTTPError, e:
            url = e.hdrs.get('Location')
        self.assertEqual('http://friedbert/wcpreview/zope.user/Somalia', url)
