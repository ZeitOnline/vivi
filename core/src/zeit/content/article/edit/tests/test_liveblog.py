from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
import zeit.content.article.testing
import zeit.edit.interfaces


class LSCDefaultTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['article'] = zeit.content.article.testing.create_article()
        with checked_out(self.repository['article']) as co:
            co.body.create_item('liveblog')
            self.assertFalse(ISemanticChange(co).has_semantic_change)

    def test_article_with_liveblog_old_has_lsc_on_checkout(self):
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
        from zeit.content.article.edit.liveblog import Liveblog
        import lxml.objectify

        liveblog = Liveblog(None, lxml.objectify.E.liveblog())
        return liveblog

    def test_liveblog_should_be_set(self):
        liveblog = self.get_liveblog()
        liveblog.blog_id = '290'
        liveblog.invalid_attribute = 'this should not be set'
        self.assertEqual('290', liveblog.xml.xpath('.')[0].get('blogID'))
        self.assertIsNone(liveblog.xml.xpath('.')[0].get('invalid_attribute'))

    def test_liveblog_version_should_be_set(self):
        liveblog = self.get_liveblog()
        self.assertIsNone(liveblog.xml.xpath('.')[0].get('version'))
        liveblog.version = '3'
        self.assertEqual('3', liveblog.xml.xpath('.')[0].get('version'))

    def test_liveblog_collapse_preceding_content_should_be_set(self):
        liveblog = self.get_liveblog()
        self.assertTrue(liveblog.collapse_preceding_content)
