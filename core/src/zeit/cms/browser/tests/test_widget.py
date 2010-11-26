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

    def test_drop_should_create_hidden_field_with_unique_id(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForElementPresent('css=input[name=testwidget.0]')
        s.assertValue('css=input[name=testwidget.0]',
                      'http://xml.zeit.de/testcontent')

    def test_drop_should_increase_count(self):
        s = self.selenium
        s.assertValue('css=input[name=testwidget.count]', '0')
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue('css=input[name=testwidget.count]', '1')
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue('css=input[name=testwidget.count]', '2')

    def test_widget_should_load_details_from_server(self):
        s = self.selenium
        s.assertElementNotPresent('css=li.element')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.waitForElementPresent('css=li.element')
        s.waitForTextPresent('2007')

    def test_delete_should_remove_text(self):
        s = self.selenium
        s.assertElementNotPresent('css=li.element')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.waitForElementPresent('css=li.element')
        s.click('css=a[rel=delete]')
        s.waitForElementNotPresent('css=li.element')

    def test_delete_should_removee_hidden_field_with_unique_id(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForElementPresent('css=input[name=testwidget.0]')
        s.click('css=a[rel=delete]')
        s.waitForElementNotPresent('css=input[name=testwidget.0]')

    def test_delete_should_decrease_count(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue('css=input[name=testwidget.count]', '1')
        s.click('css=a[rel=delete]')
        s.waitForValue('css=input[name=testwidget.count]', '0')

