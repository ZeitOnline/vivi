from zeit.content.article.article import Article
import gocept.testing.mock
import mock
import zeit.content.article.edit.interfaces
import zeit.content.article.testing


class HeaderAreaTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(HeaderAreaTest, self).setUp()
        self.patches = gocept.testing.mock.Patches()
        fake_uuid = mock.Mock()
        fake_uuid.side_effect = lambda: 'id-%s' % fake_uuid.call_count
        self.patches.add(
            'zeit.edit.container.Base._generate_block_id', fake_uuid)

    def tearDown(self):
        self.patches.reset()
        super(HeaderAreaTest, self).tearDown()

    def test_can_adapt_article_to_header(self):
        article = Article()
        header = zeit.content.article.edit.interfaces.IHeaderArea(article)
        self.assertEqual([], header.keys())

    def test_for_bw_compat_header_creates_its_xml_node_if_not_present(self):
        article = Article()
        article.xml.head.remove(article.xml.head.header)
        header = zeit.content.article.edit.interfaces.IHeaderArea(article)
        self.assertEqual([], header.keys())
        self.assertEqual(1, len(article.xml.xpath('//head/header')))

    def test_contains_at_most_one_module(self):
        article = Article()
        header = zeit.content.article.edit.interfaces.IHeaderArea(article)
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
        header = zeit.content.article.edit.interfaces.IHeaderArea(article)
        header.create_item('quiz')
        self.repository['article'] = article
        header = zeit.content.article.edit.interfaces.IHeaderArea(
            self.repository['article'])
        self.assertEqual(['quiz'], [x.type for x in header.values()])
