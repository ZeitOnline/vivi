# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class DragAndDrop(zeit.cms.testing.SeleniumTestCase):

    def start_drag(self, locator):
        s = self.selenium
        s.mouseDown(locator)
        s.mouseMoveAt(locator, '10,10')

    def test_droppable_is_activated_for_content_draggables(self):
        s = self.selenium
        self.open(
            '/@@/zeit.cms.javascript.base/tests/landingzone.html')
        self.start_drag('drag')
        s.waitForElementPresent('css=#drop.droppable-active')
