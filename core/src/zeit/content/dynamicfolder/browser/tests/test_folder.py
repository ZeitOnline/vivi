from zope.testbrowser.browser import LinkNotFoundError

import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.dynamicfolder.interfaces
import zeit.content.dynamicfolder.testing


class EditDynamicFolder(zeit.content.dynamicfolder.testing.BrowserTestCase):
    def test_check_out_and_edit_folder(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/dynamicfolder')
        b.getLink('Checkout').click()
        b.getControl('Configuration file').value = 'http://xml.zeit.de/testcontent'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        b.getLink('Checkin').click()
        self.assertIn('repository', b.url)
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamicfolder')
        self.assertEqual('http://xml.zeit.de/testcontent', folder.config_file.uniqueId)

    def test_materialize_buttons_are_not_displayed_on_default(self):
        """Both buttons belong to the materialize workflow"""
        browser = self.wsgiBrowser()
        with self.assertRaises(LinkNotFoundError):
            browser.getLink(url='@@materialize.html')
            browser.getLink(url='@@publish-content')

    def test_publish_all_content_is_diplayed_for_clone_army(self):
        browser = self.cloneArmy()
        browser.getLink(url='@@publish-content')

    def test_materialize_button_are_displayed_for_clone_army(self):
        browser = self.cloneArmy()
        link = browser.getLink(url='@@materialize.html')
        url = link.url.split("'")[1]
        browser.open(url)
        browser.getControl('Delete and materialize')
