from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
import zeit.content.article.testing
import zeit.edit.interfaces
import zope.component


class LSCDefaultTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(LSCDefaultTest, self).setUp()
        self.repository[
            'article'] = zeit.content.article.testing.create_article()
        with checked_out(self.repository['article']) as co:
            co.body.create_item('liveblog')
            self.assertFalse(ISemanticChange(co).has_semantic_change)

    def test_article_with_liveblog_has_lsc_on_checkout(self):
        with checked_out(self.repository['article']) as co:
            self.assertTrue(ISemanticChange(co).has_semantic_change)

    def test_lsc_is_not_updated_during_publish(self):
        article = self.repository['article']
        lsc = ISemanticChange(article).last_semantic_change
        zeit.cms.workflow.interfaces.IPublishInfo(article).urgent = True
        zeit.cms.workflow.interfaces.IPublish(article).publish()
        zeit.workflow.testing.run_publish()
        self.assertEqual(lsc, ISemanticChange(article).last_semantic_change)
