# coding: utf-8
from unittest import mock
import zeit.content.author.author
import zeit.content.author.interfaces
import zeit.content.author.testing
import zeit.find.interfaces
import zope.component


class HonorarLookupTest(zeit.content.author.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.patch = mock.patch('zeit.content.author.author.Author.exists')
        self.author_exists = self.patch.start()
        self.author_exists.return_value = False

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_add_author_first_searches_honorar_db(self):
        api = zope.component.getUtility(
            zeit.content.author.interfaces.IHonorar)
        api.search.return_value = [
            {'gcid': '1234', 'vorname': 'Williäm', 'nachname': 'Shakespeare'},
            {'gcid': 2345, 'vorname': 'Random', 'nachname': 'Filler'},
        ]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Firstname').value = 'föö'
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
        self.assertEllipsis("""\
            ...There were errors...
            ...An author with the given name already exists...
            """, b.contents)

        b.getControl('Add duplicate author').selected = True
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

    def test_pen_name_has_priority(self):
        api = zope.component.getUtility(
            zeit.content.author.interfaces.IHonorar)
        api.search.return_value = [
            {'gcid': '1234', 'vorname': 'Secret', 'nachname': 'Identity',
             'kuenstlervorname': 'William',
             'kuenstlernachname': 'Shakespeare'},
            {'gcid': '2345', 'vorname': 'Random', 'nachname': 'Filler'},
        ]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Firstname').value = 'foo'
        b.getControl('Lastname').value = 'bar'
        b.getControl('Look up author').click()
        b.getControl(name='selection').displayValue = ['William Shakespeare']
        b.getControl(name='action-import').click()
        self.assertEqual('William', b.getControl('Firstname').value)
        self.assertEqual('Shakespeare', b.getControl('Lastname').value)
        self.assertEqual('1234', b.getControl('Honorar ID').value)

    def test_checks_for_existing_honorar_id(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/@@zeit.content.author.add_contextfree')
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('VG-Wort ID').value = '12345'
        b.getControl('Honorar ID').value = '12345'
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        es = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        es.search.return_value = zeit.cms.interfaces.Result([{
            'url': '/author/foo',
            'payload': {'xml': {'honorar_id': 12345}}
        }])
        es.search.return_value.hits = 1
        b.getControl(name='form.actions.add').click()
        self.assertEllipsis(
            '...Author with honorar ID 12345...'
            'redirect_to?unique_id=http://xml.zeit.de/author/foo...',
            b.contents)
