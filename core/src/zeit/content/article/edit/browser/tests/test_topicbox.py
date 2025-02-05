import zeit.content.article.article
import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.create_content()

    def create_content(self):
        import zeit.content.cp.centerpage

        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.repository['foo'] = zeit.content.article.article.Article()
        self.repository['bar'] = zeit.content.article.article.Article()

    def test_topicbox_source_manual_form_saves_values(self):
        self.get_article(with_block='topicbox')
        b = self.browser
        b.open('editable-body/blockname/@@edit-topicbox?show_form=1')
        b.getControl('Title').value = 'Foo'
        b.getControl('Supertitle').value = 'Bar'
        b.getControl('Link').value = 'https://example.com'
        b.getControl('Linktext').value = 'Baz'
        b.getControl('Automatic type').displayValue = ['manual']
        b.getControl('Reference', index=0).value = 'http://xml.zeit.de/cp'
        b.getControl('Reference', index=1).value = 'http://xml.zeit.de/foo'
        b.getControl('Reference', index=2).value = 'http://xml.zeit.de/bar'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('Foo', b.getControl('Title').value)
        self.assertEqual('Bar', b.getControl('Supertitle').value)
        self.assertEqual(['manual'], b.getControl('Automatic type').displayValue)
        self.assertEqual('http://xml.zeit.de/cp', b.getControl('Reference', index=0).value)
        self.assertEqual('http://xml.zeit.de/foo', b.getControl('Reference', index=1).value)
        self.assertEqual('http://xml.zeit.de/bar', b.getControl('Reference', index=2).value)
        self.assertEqual('https://example.com', b.getControl('Link').value)
        self.assertEqual('Baz', b.getControl('Linktext').value)

    def test_topicbox_source_centerpage_form_saves_values(self):
        self.get_article(with_block='topicbox')
        b = self.browser
        b.open('editable-body/blockname/@@edit-topicbox?show_form=1')
        b.getControl('Title').value = 'Centerpage-Foo'
        b.getControl('Supertitle').value = 'Centerpage-Bar'
        b.getControl('Link').value = 'https://centerpages.com'
        b.getControl('Linktext').value = 'Centerpage-Baz'
        b.getControl('Automatic type').displayValue = ['centerpage']
        b.getControl('Get teasers from CenterPage').value = 'http://xml.zeit.de/cp'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('Centerpage-Foo', b.getControl('Title').value)
        self.assertEqual('Centerpage-Bar', b.getControl('Supertitle').value)
        self.assertEqual(['centerpage'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://centerpages.com', b.getControl('Link').value)
        self.assertEqual('Centerpage-Baz', b.getControl('Linktext').value)
        self.assertEqual('http://xml.zeit.de/cp', b.getControl('Get teasers from CenterPage').value)

    def test_topicbox_source_topicpage_form_saves_values(self):
        self.get_article(with_block='topicbox')
        b = self.browser
        b.open('editable-body/blockname/@@edit-topicbox?show_form=1')
        b.getControl('Title').value = 'Topicpage-Foo'
        b.getControl('Supertitle').value = 'Topicpage-Bar'
        b.getControl('Link').value = 'https://topicpages.com'
        b.getControl('Linktext').value = 'Topicpage-Baz'
        b.getControl('Automatic type').displayValue = ['topicpage']
        b.getControl('Referenced Topicpage').value = 'angela-merkel'
        b.getControl('Topicpage filter').value = 'videos'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('Topicpage-Foo', b.getControl('Title').value)
        self.assertEqual('Topicpage-Bar', b.getControl('Supertitle').value)
        self.assertEqual(['topicpage'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://topicpages.com', b.getControl('Link').value)
        self.assertEqual('Topicpage-Baz', b.getControl('Linktext').value)
        self.assertEqual('angela-merkel', b.getControl('Referenced Topicpage').value)
        self.assertEqual(['videos'], b.getControl('Topicpage filter').value)

    def test_topicbox_source_related_api_form_saves_values(self):
        self.get_article(with_block='topicbox')
        b = self.browser
        b.open('editable-body/blockname/@@edit-topicbox?show_form=1')
        b.getControl('Title').value = 'Related-Foo'
        b.getControl('Supertitle').value = 'Related-Bar'
        b.getControl('Link').value = 'https://related.com'
        b.getControl('Linktext').value = 'Related-Baz'
        b.getControl('Automatic type').displayValue = ['related-api']
        b.getControl('Topicpage filter').value = 'videos'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('Related-Foo', b.getControl('Title').value)
        self.assertEqual('Related-Bar', b.getControl('Supertitle').value)
        self.assertEqual(['related-api'], b.getControl('Automatic type').displayValue)
        self.assertEqual('https://related.com', b.getControl('Link').value)
        self.assertEqual('Related-Baz', b.getControl('Linktext').value)
        self.assertEqual(['videos'], b.getControl('Topicpage filter').value)
