import zeit.cms.repository.unknown
import zeit.cms.testing


class TypeChangeBoxTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_change_type(self):
        self.repository['file'] = zeit.cms.repository.unknown.PersistentUnknownResource('<empty/>')
        b = self.browser
        b.open('/repository/file')
        self.assertEllipsis('...lightbox_form...@@typechange-box...', b.getLink('Change type').url)
        b.open('@@typechange-box')
        self.assertEqual(
            ['collection', 'file', 'testcontenttype', 'unknown'],
            b.getControl(name='newtype').displayOptions,
        )

        b.getControl(name='newtype').displayValue = ['testcontenttype']
        b.getControl('Change type').click()
        self.assertEllipsis('...Type changed. Loading...', b.contents)

        self.assertEqual(
            'testcontenttype', self.repository.connector['http://xml.zeit.de/file'].type
        )


class TypeChangeBoxSeleniumTest(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def test_box_should_scroll(self):
        s = self.selenium
        self.open('/repository/testcontent')
        s.setWindowSize(1000, 300)
        s.click('css=a[title="Additional actions"]')
        s.click('link=Change type')
        s.waitForElementPresent('css=.lightbox-full')
        element = "window.jQuery('.lightbox-full')[0]"
        scroll = s.getEval(element + '.scrollHeight')
        offset = s.getEval(element + '.offsetHeight')
        self.assertGreater(scroll, offset)
