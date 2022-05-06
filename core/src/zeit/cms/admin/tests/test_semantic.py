from zeit.cms.admin.interfaces import IAdjustSemanticPublish
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import datetime
import pytz
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces


class TestSemantic(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        self.content = ExampleContentType()

    def test_adjust_semantic_publish_displays_date_last_published_semantic(
            self):
        lsc = datetime.datetime(2013, 10, 30, tzinfo=pytz.UTC)
        zeit.cms.workflow.interfaces.IPublishInfo(
            self.content).date_last_published_semantic = lsc
        self.assertEqual(
            lsc, IAdjustSemanticPublish(self.content).adjust_semantic_publish)

    def test_setting_adjust_semantic_publish_overwrites_lsc_and_dlps(self):
        lsc = datetime.datetime(2013, 10, 30, tzinfo=pytz.UTC)
        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_semantic_publish = lsc

        self.assertEqual(
            lsc, zeit.cms.workflow.interfaces.IPublishInfo(
                self.content).date_last_published_semantic)
        self.assertEqual(
            lsc, zeit.cms.content.interfaces.ISemanticChange(
                self.content).last_semantic_change)

    def test_setting_adjust_semantic_publish_overwrites_has_semantic(self):
        zeit.cms.content.interfaces.ISemanticChange(
            self.content).has_semantic_change = True

        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_semantic_publish = datetime.datetime(
            2013, 10, 30, tzinfo=pytz.UTC)

        self.assertEqual(
            False, zeit.cms.content.interfaces.ISemanticChange(
                self.content).has_semantic_change)

    def test_setting_adjust_first_released_overwrites_dfr(self):
        lsc = datetime.datetime(2013, 10, 30, tzinfo=pytz.UTC)
        semantic = IAdjustSemanticPublish(self.content)
        semantic.adjust_first_released = lsc

        self.assertEqual(
            lsc, zeit.cms.workflow.interfaces.IPublishInfo(
                self.content).date_first_released)
