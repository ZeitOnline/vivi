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

    def test_topicbox_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Title').value = 'Foo'
        b.getControl('Supertitle').value = 'Bar'
        b.getControl('Link').value = 'https://example.com'
        b.getControl('Linktext').value = 'Baz'
        b.getControl('Reference', index=0).value = 'http://xml.zeit.de/cp'
        b.getControl('Reference', index=1).value = 'http://xml.zeit.de/foo'
        b.getControl('Reference', index=2).value = 'http://xml.zeit.de/bar'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('Foo', b.getControl('Title').value)
        self.assertEqual('Bar', b.getControl('Supertitle').value)
        self.assertEqual('http://xml.zeit.de/cp',
                         b.getControl('Reference', index=0).value)
        self.assertEqual('http://xml.zeit.de/foo',
                         b.getControl('Reference', index=1).value)
        self.assertEqual('http://xml.zeit.de/bar',
                         b.getControl('Reference', index=2).value)
        self.assertEqual('https://example.com', b.getControl('Link').value)
        self.assertEqual('Baz', b.getControl('Linktext').value)
