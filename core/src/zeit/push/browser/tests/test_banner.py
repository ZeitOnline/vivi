from zeit.cms.testcontenttype.testcontenttype import TestContentType
import mock
import zeit.push.interfaces
import zeit.push.testing
import zope.component


class RetractBannerTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(RetractBannerTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            for name in ['homepage', 'ios-legacy', 'wrapper']:
                content = TestContentType()
                self.repository[name] = content
                notifier = zope.component.getUtility(
                    zeit.push.interfaces.IPushNotifier, name=name)
                notifier.uniqueId = content.uniqueId

    def tearDown(self):
        for name in ['homepage', 'ios-legacy', 'wrapper']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=name)
            del notifier.uniqueId
        super(RetractBannerTest, self).tearDown()

    def test_renders_url_for_each_banner(self):
        b = self.browser
        with mock.patch(
                'zeit.push.browser.banner.Retract.banner_matches', new=True):
            b.open('http://localhost/++skin++vivi/@@breaking-banner-retract')
        self.assertEllipsis("""\
            ...cms:context=".../repository/homepage"...
            ...cms:context=".../repository/ios-legacy"...
            ...cms:context=".../repository/wrapper"...""", b.contents)
