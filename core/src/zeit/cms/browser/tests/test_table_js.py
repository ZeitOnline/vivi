import zeit.cms.testing


class TestObjectDetailsJavascript(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def test_drag_and_drop_to_sort_table_rows(self):
        self.open('/@@/zeit.cms.browser.tests.fixtures/tabledrag.html')
        s = self.selenium
        s.dragAndDropToObject('id=one', 'id=two', '10,10')
        s.waitForOrdered('//tr[@id="two"]', '//tr[@id="one"]')
