# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import contextlib
import mock
import unittest2
import zeit.cms.testing


class TestObjectDetails(unittest2.TestCase,
                        zeit.cms.testing.FunctionalTestCase,
                        zeit.cms.testing.BrowserAssertions):

    def setUp(self):
        from zope.testbrowser.testing import Browser
        super(TestObjectDetails, self).setUp()
        self.layer.setup.setUp()
        self.browser = browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent/')

    def tearDown(self):
        self.layer.setup.tearDown()

    @contextlib.contextmanager
    def get_content(self):
        from zeit.cms.checkout.helper import checked_out
        import zeit.cms.interfaces
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                content = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/testcontent')
                with checked_out(content) as co:
                    yield co

    def test_should_contain_teaser_title(self):
        with self.get_content() as co:
            co.teaserTitle = u'test title'
        self.browser.open('@@object-details')
        self.assert_ellipsis(
            '...<div class="teaser_title">test title</div>...')

    def test_should_contain_super_title(self):
        with self.get_content() as co:
            co.supertitle = u'super'
        self.browser.open('@@object-details')
        self.assert_ellipsis(
            '...<div class="supertitle">...super...</div>...')

    def test_should_contain_workflow_information(self):
        self.browser.open('@@object-details')
        self.assert_ellipsis(
            '...class="publish-state"...Not published...')


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
                                          zeit.cms.testing.FunctionalTestCase,
                                          zeit.cms.testing.BrowserAssertions):

    def get_field(self):
        import zeit.cms.content.contentsource
        import zope.schema
        return zope.schema.Tuple(
            value_type=zope.schema.Choice(
                source=zeit.cms.content.contentsource.cmsContentSource))

    def get_widget(self, value=()):
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
        widget.setRenderedValue(value)
        return widget

    def test_widget_should_be_available_with_search(self):
        from zeit.cms.browser.widget import MultiObjectSequenceWidget
        widget = self.get_widget()
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

    def test_widget_should_render_source_query_view(self):
        import zeit.cms.content.interfaces
        import zope.component
        import zope.formlib.interfaces
        import zope.publisher.interfaces.browser
        adapter = mock.Mock()
        adapter.return_value = mock.Mock(return_value='mock')
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(
            adapter,
            (zeit.cms.content.interfaces.INamedCMSContentSource,
             zope.publisher.interfaces.browser.IBrowserRequest),
            zope.formlib.interfaces.ISourceQueryView)
        self.addCleanup(lambda: gsm.unregisterAdapter(
            adapter,
            (zeit.cms.content.interfaces.INamedCMSContentSource,
             zope.publisher.interfaces.browser.IBrowserRequest),
            zope.formlib.interfaces.ISourceQueryView))
        widget = self.get_widget()
        result = widget()
        adapter.assert_called()
        self.assert_ellipsis('...<div>mock</div>...', result)


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

class TestObjectSequenceWidgetAutocompleteJavascript(
    zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(TestObjectSequenceWidgetAutocompleteJavascript, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/'
            'objectsequencewidget-autocomplete.html')

    def test_input_should_activate_autocomplete(self):
        s = self.selenium
        s.waitForElementPresent('css=.autocomplete.ui-autocomplete-input')

    def test_input_should_autocomplete_on_type(self):
        s = self.selenium
        s.typeKeys('css=.autocomplete', 'a')
        s.waitForElementPresent('css=ul.ui-autocomplete')

    def test_selecting_autocomplete_should_add_object(self):
        s = self.selenium
        s.typeKeys('css=.autocomplete', 'a')
        s.waitForElementPresent('link=*Test Autor*')
        s.mouseOver('link=*Test Autor*')
        s.click('link=*Test Autor*')
        s.waitForElementPresent('id=testwidget.0')
        s.assertValue('id=testwidget.0',
                      'http://xml.zeit.de/autoren/A/Test_Autor/index')


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


class TestObjectSequenceDisplayWidget(unittest2.TestCase):

    def get_content(self):
        import zeit.cms.interfaces
        import zope.interface
        content = mock.Mock()
        zope.interface.alsoProvides(
            content, zeit.cms.interfaces.ICMSContent)
        return content

    def get_widget(self):
        from zeit.cms.browser.widget import MultiObjectSequenceDisplayWidget
        context = mock.Mock()
        context.__name__ = 'name'
        return MultiObjectSequenceDisplayWidget(
            context, mock.Mock(), mock.Mock())

    def test_get_values_should_ignore_non_cms_content(self):
        widget = self.get_widget()
        widget._data = (mock.sentinel.foo, mock.sentinel.bar)
        self.assertEqual([], widget.get_values())

    def test_get_values_should_returnd_data_if_set(self):
        widget = self.get_widget()
        content = self.get_content()
        content2 = self.get_content()
        widget._data = (content, content2)
        self.assertEqual([content, content2], widget.get_values())

    def test_get_values_should_returnd_default_if_no_data_set(self):
        widget = self.get_widget()
        content = self.get_content()
        content2 = self.get_content()
        widget.context.default = (content, content2)



class TestObjectSequenceDisplayWidgetIntegration(
    unittest2.TestCase,
    zeit.cms.testing.FunctionalTestCase,
    zeit.cms.testing.BrowserAssertions):

    def get_field(self):
        import zeit.cms.content.contentsource
        import zope.schema
        return zope.schema.Tuple(
            value_type=zope.schema.Choice(
                source=zeit.cms.content.contentsource.cmsContentSource))

    def get_widget(self):
        import zeit.cms.browser.interfaces
        import zope.formlib.interfaces
        import zope.interface
        import zope.publisher.browser
        field = self.get_field()
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(
            request, zeit.cms.browser.interfaces.IViviSkin)
        widget = zope.component.getMultiAdapter(
            (field, request),
            zope.formlib.interfaces.IDisplayWidget)
        return widget

    def get_content(self):
        import zeit.cms.interfaces
        return zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')

    def test_should_render_details_for_referenced_items(self):
        widget = self.get_widget()
        zeit.cms.testing.set_site(self.getRootFolder())
        content = self.get_content()
        widget._data = (content,)
        with zeit.cms.testing.interaction():
            self.assert_ellipsis(
                '...<div class="content-details...supertitle...', widget())
