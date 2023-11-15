import zeit.cms.testing


class TestClipboard(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER
    window_height = 800

    def test_adding_via_drag_and_drop(self):
        self.open('/repository')
        s = self.selenium

        # First, we need to fill the clipboard.
        # Creat clip
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('link=Clip')
        # Open clip
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        s.click('jquery=td:contains(testcontent)')
        s.waitForElementPresent('css=div#bottomcontent > div')
        s.pause(500)
        s.dragAndDropToObject('jquery=td:contains(testcontent)', '//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip/testcontent"]')
