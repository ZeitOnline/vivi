# coding: utf8
from unittest import mock
import zeit.cms.browser.interfaces
import zeit.cms.repository.browser.repository
import zeit.cms.testing
import zope.publisher.browser


class TestTree(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def test_tree_keeps_state(self):
        s = self.selenium

        # Delete the tree state cookie to have a defined starting point
        s.deleteCookie('zeit.cms.repository.treeState', '/')
        self.open('/', auth='zmgr:mgrpw')
        s.waitForElementPresent('//li[@uniqueid="http://xml.zeit.de/online/"]')

        # Open `online`
        s.clickAt('//li[@uniqueid="http://xml.zeit.de/online/"]', '10,10')
        s.waitForElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007/"]')

        # Tree is still open after reload."
        self.open('/', auth='zmgr:mgrpw')
        s.waitForElementPresent(
            '//li[@uniqueid="http://xml.zeit.de/online/2007/"]')


class TreeURLTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_handles_unicode_in_uniqueIds(self):
        UNUSED = None
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        view = zeit.cms.repository.browser.repository.HTMLTree(
            UNUSED, request, UNUSED, UNUSED)
        with mock.patch(
                'zeit.cms.repository.interfaces.IUserPreferences') as prefs:
            with mock.patch('zeit.cms.browser.tree.Tree.treeState',
                            new=['http://xml.zeit.de/bär']):
                prefs().get_hidden_containers.return_value = [
                    'http://xml.zeit.de/föö']
                self.assertEqual(
                    'http://127.0.0.1/repository/++noop++'
                    '14b688265a0bc1b8a55c8ca8b7dfb8e6/@@tree.html',
                    view.tree_url)
