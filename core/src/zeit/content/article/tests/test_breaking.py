from lxml import etree
from zeit.cms.checkout.helper import checked_out
import zeit.cms.workflow.interfaces
from zeit.content.article.interfaces import IBreakingNews
from zeit.content.article.testing import create_article
import zeit.content.article.testing
import zeit.content.rawxml.rawxml


class BreakingNewsTest(zeit.content.article.testing.FunctionalTestCase):

    def create_breaking_news_article(self):
        article = zeit.content.article.testing.create_article()
        IBreakingNews(article).is_breaking = True
        self.repository['breaking'] = article
        return self.repository['breaking']

    def test_keywords_are_not_required_for_breaking_news(self):
        breaking = self.create_breaking_news_article()
        with self.assertNothingRaised():
            with checked_out(breaking, temporary=False):
                pass

    def test_breaking_news_has_homepage_publish_priority(self):
        breaking = self.create_breaking_news_article()
        self.assertEqual(
            zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE,
            zeit.cms.workflow.interfaces.IPublishPriority(breaking)
        )
        article = zeit.content.article.testing.create_article()
        self.assertNotEqual(
            zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE,
            zeit.cms.workflow.interfaces.IPublishPriority(article)
        )


class BreakingBannerTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        banner_config = zeit.content.rawxml.rawxml.RawXML()
        banner_config.xml = etree.fromstring('<xml><article_id/></xml>')
        self.repository['banner'] = banner_config
        self.repository['article'] = create_article()

    def test_no_article_id_in_banner_config_does_not_match(self):
        self.assertFalse(
            IBreakingNews(self.repository['article']).banner_matches())

    def test_url_equal_uniqueId_matches(self):
        with checked_out(self.repository['banner']) as co:
            co.xml = etree.fromstring('<xml><article_id>'
                                      'http://xml.zeit.de/article'
                                      '</article_id></xml>')
        self.assertTrue(
            IBreakingNews(self.repository['article']).banner_matches())

    def test_url_not_equal_uniqueId_does_not_match(self):
        with checked_out(self.repository['banner']) as co:
            co.xml = etree.fromstring('<xml><article_id>'
                                      'http://xml.zeit.de/foo'
                                      '</article_id></xml>')
        self.assertFalse(
            IBreakingNews(self.repository['article']).banner_matches())
