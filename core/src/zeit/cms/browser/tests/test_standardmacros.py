from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.testing


class MainTemplateTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_passes_feature_toggles_to_javascript(self):
        b = self.browser
        b.open('/repository')
        self.assertEllipsis(
            '...var feature_toggles = {..."article_agencies": true, ...};...', b.contents
        )

        # Test overrides also work
        FEATURE_TOGGLES.unset('article_agencies')
        b.open('/repository')
        self.assertEllipsis(
            '...var feature_toggles = {..."article_agencies": false, ...};...', b.contents
        )
