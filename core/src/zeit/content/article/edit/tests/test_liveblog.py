import lxml.builder

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
from zeit.content.article.edit.liveblog import TickarooLiveblog
import zeit.content.article.testing
import zeit.edit.interfaces


class LSCDefaultTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['article'] = zeit.content.article.testing.create_article()
        with checked_out(self.repository['article']) as co:
            co.body.create_item('tickaroo_liveblog')
            self.assertFalse(ISemanticChange(co).has_semantic_change)

    def test_article_with_liveblog_has_lsc_on_checkout(self):
        with checked_out(self.repository['article']) as co:
            self.assertTrue(ISemanticChange(co).has_semantic_change)

    def test_lsc_is_not_updated_during_publish(self):
        article = self.repository['article']
        lsc = ISemanticChange(article).last_semantic_change
        zeit.cms.workflow.interfaces.IPublishInfo(article).urgent = True
        zeit.cms.workflow.interfaces.IPublish(article).publish()
        self.assertEqual(lsc, ISemanticChange(article).last_semantic_change)


class LiveblogTest(zeit.content.article.testing.FunctionalTestCase):
    def get_liveblog(self):
        liveblog = TickarooLiveblog(None, lxml.builder.E.liveblog())
        return liveblog

    def test_liveblog_should_be_set(self):
        liveblog = self.get_liveblog()
        liveblog.liveblog_id = '290'
        liveblog.invalid_attribute = 'this should not be set'
        liveblog.timeline_template = 'highlighted'
        self.assertEqual('290', liveblog.xml.xpath('.')[0].get('liveblog_id'))
        self.assertEqual('highlighted', liveblog.xml.xpath('.')[0].get('timeline_template'))
        self.assertIsNone(liveblog.xml.xpath('.')[0].get('invalid_attribute'))

    def test_liveblog_collapse_preceding_content_should_be_set(self):
        liveblog = self.get_liveblog()
        self.assertTrue(liveblog.collapse_preceding_content)
