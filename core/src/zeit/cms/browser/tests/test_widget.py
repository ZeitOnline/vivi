# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestObjectSequenceWidget(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(TestObjectSequenceWidget, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/objectsequencewidget.html')

    def test_widget_should_render_note_about_new_items(self):
        s = self.selenium
        s.waitForTextPresent(
            u'Weitere Einträge durch Drag and Drop hinzufügen')

    def test_widget_should_insert_dropped_objects(self):
        s = self.selenium
        s.assertElementNotPresent('css=li.element')
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForElementPresent('css=li.element')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.waitForElementPresent('css=li.element[index=1]')
