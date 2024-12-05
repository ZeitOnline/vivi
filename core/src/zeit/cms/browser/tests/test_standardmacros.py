from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.testing


class MainTemplateTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_passes_feature_toggles_to_javascript(self):
        b = self.browser
        b.open('/repository')
        self.assertEllipsis(
            '...var feature_toggles = {..."speech_webhook": true, ...};...', b.contents
        )

        # Test overrides also work
        FEATURE_TOGGLES.unset('speech_webhook')
        b.open('/repository')
        self.assertEllipsis(
            '...var feature_toggles = {..."speech_webhook": false, ...};...', b.contents
        )
