import zeit.cms.testing
import zeit.content.cp.testing
import zeit.content.cp.browser.testing


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
        s.click('css=.type-{} > .block-inner > .edit-bar > .delete-link'
                .format(self.name))
        s.waitForCssCount('css=.type-{}'.format(self.name), 1)


class RegionTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'region'


class AreaTest(
        ElementTestHelper,
        zeit.content.cp.testing.SeleniumTestCase):

    name = 'area'


class AreaBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(AreaBrowserTest, self).setUp()
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.open('contents')
        self.content_url = self.browser.url

    def test_can_set_layout_for_area(self):
        b = self.browser
        b.getLink('Add area').click()
        edit_url = (
            'http://localhost/++skin++cms/workingcopy/zope.user/island/'
            'body/feature/{}/edit-properties'.format('lead'))
        b.open(edit_url)
        b.getLink('Ad-Medium Rectangle').click()
        b.open(edit_url)
        self.assertEllipsis('...<a ... class="mr selected"...', b.contents)
