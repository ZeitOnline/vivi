import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.dynamicfolder.testing


class EditDynamicFolder(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.dynamicfolder.testing.DYNAMIC_LAYER

    def test_check_out_and_edit_folder(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/dynamicfolder')
        b.getLink('Checkout').click()
        b.getControl(
            'Configuration file').value = 'http://xml.zeit.de/testcontent'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        b.getLink('Checkin').click()
        self.assertIn('repository', b.url)
        folder = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/dynamicfolder')
        self.assertEqual(
            'http://xml.zeit.de/testcontent', folder.config_file.uniqueId)
