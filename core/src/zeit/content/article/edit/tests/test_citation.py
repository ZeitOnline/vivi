import zeit.edit.interfaces
import zeit.content.article.testing
import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.citation


class CitationTest(zeit.content.article.testing.FunctionalTestCase):

    def test_find_first_citation_returns_first_citation_in_article(self):
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        body.create_item('citation', 1)
        citation = zeit.content.article.edit.citation.find_first_citation(
            article)
        self.assertTrue(zeit.content.article.edit.interfaces.ICitation
                        .providedBy(citation))

    def test_find_first_citation_returns_none_of_no_citation_in_article(self):
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        body.create_item('p', 1)
        citation = zeit.content.article.edit.citation.find_first_citation(
            article)
        self.assertEqual(None, citation)
