# coding: utf-8
import mock
import zeit.content.author.testing


class HonorarLookupTest(zeit.content.author.testing.BrowserTestCase):

    def setUp(self):
        super(HonorarLookupTest, self).setUp()
        self.patch = mock.patch(
            'zeit.content.author.author.Author.exists', mock.PropertyMock())
        self.patch.start().return_value = False

    def tearDown(self):
        self.patch.stop()
        super(HonorarLookupTest, self).tearDown()

    def test_add_author_first_searches_honorar_db(self):
        api = self.layer['honorar_mock']
        api.search.return_value = [{
            'gcid': '1234', 'vorname': u'Williäm', 'nachname': 'Shakespeare'}]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Name').value = 'foo'
        b.getControl('Look up author').click()
        b.getLink('Shakespeare').click()
        self.assertEqual('Williäm', b.getControl('Firstname').value)
        self.assertEqual('Shakespeare', b.getControl('Lastname').value)
        self.assertEqual('1234', b.getControl('Honorar ID').value)
