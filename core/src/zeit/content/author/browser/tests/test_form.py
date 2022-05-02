# coding: utf8
from unittest import mock
from zeit.cms.content.sources import FEATURE_TOGGLES
import unittest
import zeit.content.author.testing


class PropertyMock(mock.Mock):

    def __get__(self, instance, owner):
        return self()


class FormTest(zeit.content.author.testing.BrowserTestCase):

    def setUp(self):
        super(FormTest, self).setUp()
        self.author_exists = mock.Mock()
        self.patch = mock.patch(
            'zeit.content.author.author.Author.exists', self.author_exists)
        self.author_exists.return_value = False
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        super(FormTest, self).tearDown()

    def open(self, tail):
        self.browser.open('http://localhost/++skin++vivi' + tail)

    def test_adding_name_twice_warns_then_creates_different_author(self):
        FEATURE_TOGGLES.unset('author_lookup_in_hdok')
        b = self.browser
        self.open('/@@zeit.content.author.add_contextfree')
        self.add_william()
        self.author_exists.return_value = True

        self.open('/@@zeit.content.author.add_contextfree')
        self.assertNotIn('Add duplicate author', b.contents)
        self.add_william(vgwort_id='9876')
        self.assertEllipsis("""\
            ...There were errors...
            ...An author with the given name already exists...
            """, b.contents)
        # No new author has been created in DAV so far.
        self.assertEqual(1, len(self.repository['foo']['bar']['authors']['S']))

        b.getControl('Add duplicate author').selected = True
        b.getControl(name='form.actions.add').click()
        self.assertNotIn('There were errors', b.contents)
        # Make sure the new author gets a new __name__ rather than overwriting
        # the existing one.
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

    def add_william(self, browser=None, vgwort_id='12345'):
        b = self.browser if browser is None else browser
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('VG-Wort ID').value = vgwort_id
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()

    def add_joerg(self):
        b = self.browser
        b.getControl('Firstname').value = 'Jörg'
        b.getControl('Lastname').value = 'Müßig, von'
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()

    def test_add_form(self):
        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        b.login('producer', 'producerpw')
        b.open('http://localhost/++skin++vivi/repository/online/2007/01')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Author']
        b.open(menu.value[0])
        b.getControl('File name').value = 'william_shakespeare'
        b.getControl('Email address').value = 'wil.i.am@shakespeare.name'
        self.add_william(b)
        b.getLink('Checkin').click()
        self.assertEllipsis("""...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwortid">...
            <div class="widget">12345</div>...
            """, b.contents)
        b.getLink('Checkout').click()
        b.getControl('VG-Wort ID').value = 'flub'
        b.getControl('Apply').click()
        self.assertEllipsis('...Invalid integer data...', b.contents)

    def test_context_free_add_form(self):
        # Authors provide an add form that can be called from anywhere
        # (without a folder context), that places the resulting author objects
        # in the folder ``/<authors>/<X>/Firstname_Lastname/index`` where
        # authors is a configurable path and X the first character of the
        # lastname (uppercased).
        b = self.browser
        self.open('/@@zeit.content.author.add_contextfree')
        self.assertNotIn('File name', b.contents)
        self.add_william()
        self.assertEqual(
            'http://localhost/++skin++vivi/repository/foo/bar/authors/S/'
            'William_Shakespeare/index/@@view.html', b.url)
        self.assertEllipsis("""...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwortid">...
            <div class="widget">12345</div>...
            """, b.contents)

    def test_folder_name_validation(self):
        b = self.browser
        self.open('/@@zeit.content.author.add_contextfree')
        self.assertNotIn('File name', b.contents)
        self.add_joerg()
        self.assertEqual(
            'http://localhost/++skin++vivi/repository/foo/bar/authors/M/'
            'Joerg_Muessig-von/index/@@view.html', b.url)

    def test_folder_listing_after_adding_author(self):
        b = self.browser
        self.open('/@@zeit.content.author.add_contextfree')
        self.add_william()
        self.open('/repository/foo/bar/authors/S/William_Shakespeare/')
        self.assertEllipsis("""...
            <td>
              William Shakespeare
            </td>...
            """, b.contents)

    @unittest.skip('needs to use Selenium to control ObjectSequenceWidget')
    def test_security_smoke_test(self):
        b = self.browser
        self.open('/repository/testcontent')
        b.getLink('Checkout').click()
        b.getControl('Add Authors', index=0).click()

        b.getControl(name='form.authorships.0.').value = (
            'http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare-2/index')
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        self.assertEllipsis(
            '..."testcontent" has been checked in...', b.contents)

    def test_invalid_vgwortcode_shows_error_message(self):
        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        b.login('producer', 'producerpw')
        b.open('http://localhost/++skin++vivi/repository/online/2007/01')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Author']
        b.open(menu.value[0])
        b.getControl('File name').value = 'william_shakespeare'
        b.getControl('Email address').value = 'wil.i.am@shakespeare.name'
        b.getControl('VG-Wort Code').value = '4711'
        self.add_william(b)
        self.assertEllipsis(
            '...Code contains invalid characters...', b.contents)

    def test_stores_biography_questions(self):
        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        b.login('producer', 'producerpw')
        b.open('http://localhost/++skin++vivi/repository/online/2007/01')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Author']
        b.open(menu.value[0])
        b.getControl('File name').value = 'william_shakespeare'
        self.add_william(b)
        b.getControl('Das treibt mich an').value = 'answer'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual('answer', b.getControl('Das treibt mich an').value)
