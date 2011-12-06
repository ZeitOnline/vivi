# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.author.testing


class FormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.author.testing.ZCMLLayer

    def open(self, tail):
        self.browser.open('http://localhost/++skin++vivi' + tail)

    def add_william(self, vgwort_id='12345'):
        b = self.browser
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('VG-Wort ID').value = vgwort_id
        b.getControl('Status').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()

    def test_add_form(self):
        b = self.browser
        self.open('/repository/online/2007/01')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Author']
        b.open(menu.value[0])
        b.getControl('File name').value = 'william_shakespeare'
        b.getControl('Email address').value = 'wil.i.am@shakespeare.name'
        self.add_william()
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
        self.assertEllipsis("""...
            <span class="result">http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare/index</span>
            ...""", b.contents)
        self.open('/repository/foo/bar/authors/S/William_Shakespeare/index')
        self.assertEllipsis("""...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwortid">...
            <div class="widget">12345</div>...
            """, b.contents)

    def test_adding_name_twice_creates_different_folder(self):
        b = self.browser
        self.open('/@@zeit.content.author.add_contextfree')
        self.add_william()
        self.open('/@@zeit.content.author.add_contextfree')
        self.add_william(vgwort_id='9876')
        self.assertEllipsis("""...
            <span class="result">http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare-2/index</span>
            ...""", b.contents)
        self.open('/repository/foo/bar/authors/S/William_Shakespeare-2/index')
        self.assertEllipsis("""...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwortid">...
            <div class="widget">9876</div>...
            """, b.contents)

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

    def test_security_smoke_test(self):
        b = self.browser
        self.open('/repository/testcontent')
        b.getLink('Checkout').click()
        b.getControl('Add Authors', index=0).click()

        #XXX disabled until the fields are available again.
        # b.getControl(name='form.author_references.0.').value = (
        #     'http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare-2/index')
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        self.assertEllipsis(
            '..."testcontent" has been checked in...', b.contents)
