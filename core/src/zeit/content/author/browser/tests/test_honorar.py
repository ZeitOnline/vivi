# coding: utf-8
import mock
import zeit.content.author.author
import zeit.content.author.testing


class HonorarLookupTest(zeit.content.author.testing.BrowserTestCase):

    def setUp(self):
        super(HonorarLookupTest, self).setUp()
        self.patch = mock.patch('zeit.content.author.author.Author.exists')
        self.author_exists = self.patch.start()
        self.author_exists.return_value = False

    def tearDown(self):
        self.patch.stop()
        super(HonorarLookupTest, self).tearDown()

    def test_add_author_first_searches_honorar_db(self):
        api = self.layer['honorar_mock']
        api.search.return_value = [
            {'gcid': '1234', 'vorname': u'Williäm', 'nachname': 'Shakespeare'},
            {'gcid': '2345', 'vorname': 'Random', 'nachname': 'Filler'},
        ]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Firstname').value = 'foo'
        b.getControl('Lastname').value = 'bar'
        b.getControl('Look up author').click()
        b.getControl(name='selection').displayValue = ['Williäm Shakespeare']
        b.getControl(name='action-import').click()
        self.assertEqual('Williäm', b.getControl('Firstname').value)
        self.assertEqual('Shakespeare', b.getControl('Lastname').value)
        self.assertEqual('1234', b.getControl('Honorar ID').value)

    def test_adding_name_twice_warns_then_creates_different_author(self):
        folder = zeit.cms.content.add.find_or_create_folder(
            'foo', 'bar', 'authors', 'S', 'William_Shakespeare')
        folder['index'] = zeit.content.author.author.Author()
        self.author_exists.return_value = True

        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        self.assertNotIn('Add duplicate author', b.contents)
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('Look up author').click()
        self.assertEllipsis(u"""\
            ...There were errors...
            ...An author with the given name already exists...
            """, b.contents)

        b.getControl(u'Add duplicate author').selected = True
        b.getControl('Look up author').click()
        self.assertNotIn('There were errors', b.contents)

        # Make sure the new author gets a new __name__ rather than overwriting
        # the existing one.
        b.getControl('VG-Wort ID').value = '9876'
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()

        self.assertEqual(
            'http://localhost/++skin++vivi/repository/foo/bar/authors/S/'
            'William_Shakespeare-2/index/@@view.html', b.url)
        self.assertEllipsis("""...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwortid">...
            <div class="widget">9876</div>...
            """, b.contents)
