# coding: utf-8
import lxml.cssselect
import z3c.etestbrowser.testing
import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.testing


class ElementTestHelper(object):
    """Helper class to test creation and deletion of IRegion and IArea"""

    name = NotImplemented

    def setUp(self):
        super(ElementTestHelper, self).setUp()
        self.open_centerpage()

    def test_add_element_creates_new_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), 2)
        s.click('link=*Add {}*'.format(self.name))
        s.waitForCssCount('css=.type-{}'.format(self.name), 3)

    def test_delete_element_removes_element(self):
        s = self.selenium
        s.assertCssCount('css=.type-{}'.format(self.name), 2)
        s.chooseOkOnNextConfirmation()
        s.click('css=.type-{} > .block-inner > .edit-bar > .delete-link'
                .format(self.name))
        s.waitForConfirmation(u'Wirklich löschen?')
        s.waitForCssCount('css=.type-{}'.format(self.name), 1)


class RegionTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'region'


class AreaTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'area'


class ElementBrowserTestHelper(object):

    name = NotImplemented

    def setUp(self):
        super(ElementBrowserTestHelper, self).setUp()
        self.browser = z3c.etestbrowser.testing.ExtendedTestBrowser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        self.browser.xml_strict = True
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.open('contents')
        self.content_url = self.browser.url

    def get_edit_link(self, index=0):
        self.browser.open(self.content_url)
        return lxml.cssselect.CSSSelector(
            '.type-{} .edit-bar > .common-link'.format(
                self.name))(self.browser.etree)[index].get('href')

    def test_can_set_title(self):
        b = self.browser
        b.open(self.get_edit_link())
        b.getControl('Title').value = 'FooBarBaz'
        b.getControl('Apply').click()

        b.open(self.get_edit_link())
        self.assertEqual('FooBarBaz', b.getControl('Title').value)

    def test_can_set_name(self):
        b = self.browser
        b.open(self.get_edit_link())
        b.getControl('Name').value = 'FooBarBaz'
        b.getControl('Apply').click()

        b.open(self.get_edit_link())
        self.assertEqual('FooBarBaz', b.getControl('Name').value)

    def test_cannot_use_the_same_name_multiple_times(self):
        b = self.browser
        b.getLink('Add {}'.format(self.name)).click()
        b.open(self.content_url)
        b.getLink('Add {}'.format(self.name)).click()

        b.open(self.get_edit_link(index=0))
        b.getControl('Name').value = 'FooBarBaz'
        b.getControl('Apply').click()

        b.open(self.get_edit_link(index=1))
        b.getControl('Name').value = 'FooBarBaz'
        b.handleErrors = False
        b.getControl('Apply').click()

        self.assertIn(
            'Given name FooBarBaz is not unique inside parent', b.contents)


class RegionBrowserTest(
        ElementBrowserTestHelper,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    name = 'region'


class AreaBrowserTest(
        ElementBrowserTestHelper,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    name = 'area'

    def test_can_set_layout_for_area(self):
        b = self.browser
        b.getLink('Add {}'.format(self.name)).click()
        edit_url = (
            'http://localhost/++skin++cms/workingcopy/zope.user/island/'
            'body/feature/{}/edit-properties'.format('lead'))
        b.open(edit_url)
        b.getLink('Ad-Medium Rectangle').click()
        b.open(edit_url)
        self.assertEllipsis('...<a ... class="mr selected"...', b.contents)
