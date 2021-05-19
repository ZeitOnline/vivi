import zeit.content.article.edit.browser.testing
import zeit.content.article.article


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'topicbox'

    def setUp(self):
        super(Form, self).setUp()
        self.create_content()

    def create_content(self):
        import zeit.content.cp.centerpage
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.repository['foo'] = zeit.content.article.article.Article()
        self.repository['bar'] = zeit.content.article.article.Article()

    def test_topicbox_source_manual_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Foo'
        b.getControl('Supertitle').value = 'Bar'
        b.getControl('Link').value = 'https://example.com'
        b.getControl('Linktext').value = 'Baz'
        b.getControl('Automatic type').displayValue = ['manual']
        b.getControl('Reference', index=0).value = 'http://xml.zeit.de/cp'
        b.getControl('Reference', index=1).value = 'http://xml.zeit.de/foo'
        b.getControl('Reference', index=2).value = 'http://xml.zeit.de/bar'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Foo', b.getControl('Title').value)
        self.assertEqual('Bar', b.getControl('Supertitle').value)
        self.assertEqual([
            'manual'], b.getControl('Automatic type').displayValue)
        self.assertEqual('http://xml.zeit.de/cp',
                         b.getControl('Reference', index=0).value)
        self.assertEqual('http://xml.zeit.de/foo',
                         b.getControl('Reference', index=1).value)
        self.assertEqual('http://xml.zeit.de/bar',
                         b.getControl('Reference', index=2).value)
        self.assertEqual('https://example.com', b.getControl('Link').value)
        self.assertEqual('Baz', b.getControl('Linktext').value)

    def test_topicbox_source_centerpage_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Centerpage-Foo'
        b.getControl('Supertitle').value = 'Centerpage-Bar'
        b.getControl('Link').value = 'https://centerpages.com'
        b.getControl('Linktext').value = 'Centerpage-Baz'
        b.getControl('Automatic type').displayValue = ['centerpage']
        b.getControl(
            'Get teasers from CenterPage').value = 'http://xml.zeit.de/cp'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Centerpage-Foo', b.getControl('Title').value)
        self.assertEqual('Centerpage-Bar', b.getControl('Supertitle').value)
        self.assertEqual([
            'centerpage'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://centerpages.com', b.getControl('Link').value)
        self.assertEqual('Centerpage-Baz', b.getControl('Linktext').value)
        self.assertEqual(
            'http://xml.zeit.de/cp',
            b.getControl('Get teasers from CenterPage').value)

    def test_topicbox_source_topicpage_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Topicpage-Foo'
        b.getControl('Supertitle').value = 'Topicpage-Bar'
        b.getControl('Link').value = 'https://topicpages.com'
        b.getControl('Linktext').value = 'Topicpage-Baz'
        b.getControl('Automatic type').displayValue = ['topicpage']
        b.getControl('Referenced Topicpage').value = 'angela-merkel'
        b.getControl('Topicpage filter').value = 'videos'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Topicpage-Foo', b.getControl('Title').value)
        self.assertEqual('Topicpage-Bar', b.getControl('Supertitle').value)
        self.assertEqual([
            'topicpage'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://topicpages.com', b.getControl('Link').value)
        self.assertEqual('Topicpage-Baz', b.getControl('Linktext').value)
        self.assertEqual(
            'angela-merkel', b.getControl('Referenced Topicpage').value)
        self.assertEqual(['videos'], b.getControl('Topicpage filter').value)

    def test_topicbox_source_elasticsearch_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'ES-Foo'
        b.getControl('Supertitle').value = 'ES-Bar'
        b.getControl('Link').value = 'https://queries-es.com'
        b.getControl('Linktext').value = 'ES-Baz'
        b.getControl('Automatic type').displayValue = ['elasticsearch-query']
        es_query = '''{"query": {"term": {"doc_type": "article"}}}'''
        b.getControl('Elasticsearch raw query').value = es_query
        b.getControl('Sort order').value = 'asc'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('ES-Foo', b.getControl('Title').value)
        self.assertEqual('ES-Bar', b.getControl('Supertitle').value)
        self.assertEqual(
            ['elasticsearch-query'],
            b.getControl('Automatic type').displayValue)
        self.assertEqual('https://queries-es.com', b.getControl('Link').value)
        self.assertEqual('ES-Baz', b.getControl('Linktext').value)
        self.assertEqual(
            es_query, b.getControl('Elasticsearch raw query').value)
        self.assertEqual('asc', b.getControl('Sort order').value)

    def test_topicbox_source_related_api_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Related-Foo'
        b.getControl('Supertitle').value = 'Related-Bar'
        b.getControl('Link').value = 'https://related.com'
        b.getControl('Linktext').value = 'Related-Baz'
        b.getControl('Automatic type').displayValue = ['related-api']
        b.getControl('Filter').displayValue = ['(nothing selected)']
        b.getControl('Topicpage filter').value = 'videos'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Related-Foo', b.getControl('Title').value)
        self.assertEqual('Related-Bar', b.getControl('Supertitle').value)
        self.assertEqual([
            'related-api'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://related.com', b.getControl('Link').value)
        self.assertEqual('Related-Baz', b.getControl('Linktext').value)
        self.assertEqual(
            ['(nothing selected)'], b.getControl('Filter').displayValue)
        self.assertEqual(['videos'], b.getControl('Topicpage filter').value)

    def test_topicbox_source_config_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Config-Foo'
        b.getControl('Supertitle').value = 'Config-Bar'
        b.getControl('Link').value = 'https://config.com'
        b.getControl('Linktext').value = 'Config-Baz'
        b.getControl('Automatic type').displayValue = ['preconfigured-query']
        b.getControl('Filter').displayValue = ['(nothing selected)']
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Config-Foo', b.getControl('Title').value)
        self.assertEqual('Config-Bar', b.getControl('Supertitle').value)
        self.assertEqual(
            ['preconfigured-query'],
            b.getControl('Automatic type').displayValue)
        self.assertEqual('https://config.com', b.getControl('Link').value)
        self.assertEqual('Config-Baz', b.getControl('Linktext').value)
        self.assertEqual(
            ['(nothing selected)'], b.getControl('Filter').displayValue)
