from unittest import mock
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.push.testing


class RetractBannerTest(zeit.push.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        # production uses a rawxml object, but we can cheat here.
        self.repository['banner'] = ExampleContentType()

    def test_renders_url_for_each_banner(self):
        b = self.browser
        with mock.patch(
                'zeit.push.browser.banner.Retract.banner_matches', new=True):
            b.open('http://localhost/++skin++vivi/@@breaking-banner-retract')
        self.assertEllipsis("""\
            ...cms:context=".../repository/banner"...""", b.contents)
