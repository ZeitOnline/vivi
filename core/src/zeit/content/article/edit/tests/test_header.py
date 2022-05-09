from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.content.article.article import Article
import gocept.testing.mock
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zope.security.proxy


class HeaderAreaTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.patches = gocept.testing.mock.Patches()
        fake_uuid = mock.Mock()
        fake_uuid.side_effect = lambda: 'id-%s' % fake_uuid.call_count
        self.patches.add(
            'zeit.edit.container.Base._generate_block_id', fake_uuid)

    def tearDown(self):
        self.patches.reset()
        super().tearDown()

    def test_can_adapt_article_to_header(self):
        article = Article()
        self.assertEqual([], article.header.keys())

    def test_for_bw_compat_header_creates_its_xml_node_if_not_present(self):
        article = Article()
        article.xml.head.remove(article.xml.head.header)
        self.assertEqual([], article.header.keys())
        self.assertEqual(1, len(article.xml.xpath('//head/header')))

    def test_migration_works_with_security(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article, temporary=False) as co:
            co = zope.security.proxy.ProxyFactory(co)
            with self.assertNothingRaised():
                co.header

    def test_contains_at_most_one_module(self):
        article = Article()
        header = article.header
        header.create_item('quiz')
        self.assertEqual(['quiz'], [x.type for x in header.values()])
        self.assertEqual('quiz', header.module.type)
        header.create_item('cardstack')
        self.assertEqual(['cardstack'], [x.type for x in header.values()])
        self.assertEqual('cardstack', header.module.type)

    def test_module_is_accessible_after_checkin(self):
        # On checkin, the cp:__name__ attributes are removed, so the header
        # needs to be able to function without them.
        article = Article()
        article.header.create_item('quiz')
        self.repository['article'] = article
        header = self.repository['article'].header
        self.assertEqual(['quiz'], [x.type for x in header.values()])

    def test_index_is_implemented_via_values(self):
        article = Article()
        module = article.header.create_item('quiz')
        self.repository['article'] = article
        header = self.repository['article'].header
        self.assertEqual(0, header.index(module))

    def test_header_has_security_declaration(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article, temporary=False) as co:
            co = zope.security.proxy.ProxyFactory(co)
            with self.assertNothingRaised():
                co.header.clear()
