from pendulum import datetime

from zeit.cms.admin.interfaces import IAdjustSemanticPublish
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces


class TestSemantic(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.content = ExampleContentType()

    def test_adjust_semantic_publish_displays_date_last_published_semantic(self):
        lsc = datetime(2013, 10, 30)
        zeit.cms.workflow.interfaces.IPublishInfo(self.content).date_last_published_semantic = lsc
        self.assertEqual(lsc, IAdjustSemanticPublish(self.content).adjust_semantic_publish)

    def test_setting_adjust_semantic_publish_overwrites_lsc_and_dlps(self):
        lsc = datetime(2013, 10, 30)
        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_semantic_publish = lsc

        self.assertEqual(
            lsc,
            zeit.cms.workflow.interfaces.IPublishInfo(self.content).date_last_published_semantic,
        )
        self.assertEqual(
            lsc, zeit.cms.content.interfaces.ISemanticChange(self.content).last_semantic_change
        )

    def test_setting_adjust_semantic_publish_overwrites_has_semantic(self):
        zeit.cms.content.interfaces.ISemanticChange(self.content).has_semantic_change = True

        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_semantic_publish = datetime(2013, 10, 30)

        self.assertEqual(
            False, zeit.cms.content.interfaces.ISemanticChange(self.content).has_semantic_change
        )

    def test_setting_adjust_first_released_overwrites_dfr(self):
        lsc = datetime(2013, 10, 30)
        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_first_released = lsc

        self.assertEqual(
            lsc, zeit.cms.workflow.interfaces.IPublishInfo(self.content).date_first_released
        )
