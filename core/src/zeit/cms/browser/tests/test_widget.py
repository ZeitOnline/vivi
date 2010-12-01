# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing


class TestObjectSequenceWidget(unittest2.TestCase):

    def test_to_form_value_ignores_non_cms_content(self):
        from zeit.cms.browser.widget import MultiObjectSequenceWidget
        import zeit.cms.interfaces
        import zope.interface
        context = mock.Mock()
        context.__name__ = 'name'
        widget = MultiObjectSequenceWidget(
            context, mock.Mock(), mock.Mock())
        content = mock.Mock()
        zope.interface.alsoProvides(content, zeit.cms.interfaces.ICMSContent)
        result = widget._toFormValue([mock.sentinel.foo, content])
        self.assertEqual([{'uniqueId': content.uniqueId}], result)

    def test_to_field_value_ignores_non_cms_content(self):
        from zeit.cms.browser.widget import MultiObjectSequenceWidget
        import zeit.cms.interfaces
        import zope.interface
        context = mock.Mock()
        context.__name__ = 'name'
        widget = MultiObjectSequenceWidget(
            context, mock.Mock(), mock.Mock())
        self.assertEqual(
            (), widget._toFieldValue([mock.sentinel.foo, mock.sentinel.bar]))


class TestObjectSequenceWidgetIntegration(unittest2.TestCase,
                                          zeit.cms.testing.FunctionalTestCase):

    def get_field(self):
        import zeit.cms.content.contentsource
        import zope.schema
        return zope.schema.Tuple(
            value_type=zope.schema.Choice(
                source=zeit.cms.content.contentsource.cmsContentSource))

    def test_widget_should_be_available_with_search(self):
        from zeit.cms.browser.widget import MultiObjectSequenceWidget
        import zeit.cms.browser.interfaces
        import zope.app.form.browser.interfaces
        import zope.interface
        import zope.publisher.browser
        field = self.get_field()
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(
            request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        widget = zope.component.getMultiAdapter(
            (field, request),
            zope.app.form.browser.interfaces.IInputWidget)
        self.assertIsInstance(widget, MultiObjectSequenceWidget)

    def test_widget_should_not_be_available_without_search(self):
        from zeit.cms.browser.widget import MultiObjectSequenceWidget
        import zope.app.form.browser.interfaces
        import zope.publisher.browser
        field = self.get_field()
        request = zope.publisher.browser.TestRequest()
        widget = zope.component.getMultiAdapter(
            (field, request),
            zope.app.form.browser.interfaces.IInputWidget)
        self.assertNotIsInstance(widget, MultiObjectSequenceWidget)


class TestObjectSequenceWidgetJavascript(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(TestObjectSequenceWidgetJavascript, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/objectsequencewidget.html')

    def test_widget_should_render_note_about_new_items(self):
        s = self.selenium
        s.waitForTextPresent(
            u'Ziehen Sie Inhalte hierher um sie zu verknüpfen.')

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

    def test_remove_should_remove_text(self):
        s = self.selenium
        s.assertElementNotPresent('css=li.element')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.waitForElementPresent('css=li.element')
        s.click('css=a[rel=remove]')
        s.waitForElementNotPresent('css=li.element')

    def test_remove_should_removee_hidden_field_with_unique_id(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForElementPresent('css=input[name=testwidget.0]')
        s.click('css=a[rel=remove]')
        s.waitForElementNotPresent('css=input[name=testwidget.0]')

    def test_remove_should_decrease_count(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue('css=input[name=testwidget.count]', '1')
        s.waitForElementPresent('css=a[rel=remove]')
        s.click('css=a[rel=remove]')
        s.waitForValue('css=input[name=testwidget.count]', '0')

    def test_elements_should_be_sortable(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.assertOrdered('css=li.element[index=0]', 'css=li.element[index=1]')
        s.dragAndDropToObject('css=li.element[index=0]',
                              'css=li.element[index=1]')
        s.assertOrdered('css=li.element[index=1]', 'css=li.element[index=0]')

    def test_sorting_should_update_hidden_field_indexes(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.dragAndDropToObject('id=drag2', 'id=testwidget')
        s.assertValue('css=input[name=testwidget.0]',
                      'http://xml.zeit.de/testcontent')
        s.assertValue('css=input[name=testwidget.1]',
                      'http://xml.zeit.de/2007')
        s.dragAndDropToObject('css=li.element[index=0]',
                              'css=li.element[index=1]')
        s.assertValue('css=input[name=testwidget.0]',
                      'http://xml.zeit.de/2007')
        s.assertValue('css=input[name=testwidget.1]',
                      'http://xml.zeit.de/testcontent')



class TestDropObjectWidget(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(TestDropObjectWidget, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/dropobjectwidget.html')

    def test_no_value_should_create_landing_zone(self):
        s = self.selenium
        s.waitForElementPresent('css=#testwidget.landing-zone')

    def test_drop_should_set_input_value(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue('name=testwidget',
                       'http://xml.zeit.de/testcontent')

    def test_remove_should_clear_input_value(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForNotValue('name=testwidget', '')
        s.waitForElementPresent('css=#testwidget a')
        s.click('css=#testwidget a')
        s.waitForValue('name=testwidget', '')


class TestDropObjectWidgetIntegration(unittest2.TestCase,
                                      zeit.cms.testing.FunctionalTestCase):

    def get_choice(self):
        import zeit.cms.content.contentsource
        import zope.schema
        return zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource)

    def test_widget_should_be_available_with_search(self):
        from zeit.cms.browser.widget import DropObjectWidget
        import zeit.cms.browser.interfaces
        import zope.app.form.browser.interfaces
        import zope.interface
        import zope.publisher.browser
        choice = self.get_choice()
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(
            request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        widget = zope.component.getMultiAdapter(
            (choice, request),
            zope.app.form.browser.interfaces.IInputWidget)
        self.assertIsInstance(widget, DropObjectWidget)

    def test_widget_should_not_be_available_without_search(self):
        from zeit.cms.browser.widget import DropObjectWidget
        import zope.app.form.browser.interfaces
        import zope.publisher.browser
        choice = self.get_choice()
        request = zope.publisher.browser.TestRequest()
        widget = zope.component.getMultiAdapter(
            (choice, request),
            zope.app.form.browser.interfaces.IInputWidget)
        self.assertNotIsInstance(widget, DropObjectWidget)
