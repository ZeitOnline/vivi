from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
from zeit.content.article.edit.interfaces import IEditableBody
import zeit.content.article.testing
import zeit.edit.interfaces
import zope.component


class LSCDefaultTest(zeit.content.article.testing.FunctionalTestCase):

    def test_article_with_liveblog_has_lsc_on_checkout(self):
        self.repository[
            'article'] = zeit.content.article.testing.create_article()
        with checked_out(self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, name='liveblog')
            factory()
            self.assertFalse(ISemanticChange(co).has_semantic_change)

        with checked_out(self.repository['article']) as co:
            self.assertTrue(ISemanticChange(co).has_semantic_change)
