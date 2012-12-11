import zeit.edit.testing


class DroppableRegistration(zeit.edit.testing.SeleniumTestCase):

    def setUp(self):
        super(DroppableRegistration, self).setUp()
        self.open(
            '/@@/zeit.edit.browser.tests.fixtures/content-drop/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')
        self.eval("""\
zeit.edit.drop.Droppable.prototype.drop = function(){
    zeit.edit.dropped = true;
};
""")

    def test_registered_droppable_can_be_dropped(self):
        self.selenium.dragAndDropToObject(
            'css=#drag-foo', 'css=.foo-droppable')
        self.assertEqual('true', self.eval('Boolean(zeit.edit.dropped)'))

    def test_unregistered_droppable_cannot_be_dropped(self):
        self.selenium.dragAndDropToObject(
            'css=#drag-bar', 'css=.foo-droppable')
        self.assertEqual('false', self.eval('Boolean(zeit.edit.dropped)'))


class DragIntegration(zeit.edit.testing.SeleniumTestCase):

    def setUp(self):
        super(DragIntegration, self).setUp()
        self.open(
            '/@@/zeit.edit.browser.tests.fixtures/content-drop/editor.html')
        self.wait_for_condition('!zeit.edit.editor.busy')

    def test_landing_zones_are_reactivated_after_reload_while_dragging(self):
        s = self.selenium
        draggable = 'css=#drag-foo'
        s.mouseDown(draggable)
        s.mouseMoveAt(draggable, '10,10')
        s.assertElementPresent('css=.landing-zone.droppable-active')
        self.eval('zeit.edit.editor.reload("cp-content-inner", "contents");')
        self.wait_for_condition('!zeit.edit.editor.busy')
        s.waitForElementPresent('css=.landing-zone.droppable-active')
