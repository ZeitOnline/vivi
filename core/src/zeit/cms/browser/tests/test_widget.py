# coding: utf8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.browser.widget import \
    ObjectSequenceWidget, ObjectSequenceDisplayWidget
import contextlib
import mock
import unittest2
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.cms.testing
import zope.configuration.xmlconfig
import zope.formlib.interfaces


class TestObjectDetails(zeit.cms.testing.BrowserTestCase):

    def setUp(self):
        super(TestObjectDetails, self).setUp()
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent/')

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
        import zeit.cms.interfaces
        import zope.interface
        context = mock.Mock()
        context.__name__ = 'name'
        widget = ObjectSequenceWidget(context, mock.Mock(), mock.Mock())
        content = mock.Mock()
        zope.interface.alsoProvides(content, zeit.cms.interfaces.ICMSContent)
        result = widget._toFormValue([mock.sentinel.foo, content])
        self.assertEqual([{'uniqueId': content.uniqueId}], result)

    def test_to_field_value_ignores_non_cms_content(self):
        context = mock.Mock()
        context.__name__ = 'name'
        widget = ObjectSequenceWidget(context, mock.Mock(), mock.Mock())
        self.assertEqual(
            (), widget._toFieldValue([mock.sentinel.foo, mock.sentinel.bar]))

    def test_to_form_value_copes_with_none(self):
        context = mock.Mock()
        context.__name__ = 'name'
        widget = ObjectSequenceWidget(context, mock.Mock(), mock.Mock())
        self.assertEqual([], widget._toFormValue(None))


class TestObjectSequenceWidgetIntegration(zeit.cms.testing.FunctionalTestCase,
                                          zeit.cms.testing.BrowserAssertions):

    def setUp(self):
        import zope.security.management
        super(TestObjectSequenceWidgetIntegration, self).setUp()
        zope.security.management.endInteraction()

    def get_field(self):
        import zeit.cms.content.contentsource
        import zope.schema
        return zope.schema.Tuple(
            value_type=zope.schema.Choice(
                source=zeit.cms.content.contentsource.cmsContentSource))

    def get_widget(self, field=None):
        import zeit.cms.browser.interfaces
        import zope.app.form.browser.interfaces
        import zope.interface
        import zope.publisher.browser
        if field is None:
            field = self.get_field()
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(
            request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        widget = zope.component.getMultiAdapter(
            (field, request),
            zope.app.form.browser.interfaces.IInputWidget)
        widget.setRenderedValue(())
        return widget

    def test_widget_should_be_available_with_search(self):
        widget = self.get_widget()
        self.assertIsInstance(widget, ObjectSequenceWidget)

    def test_widget_should_not_be_available_without_search(self):
        import zope.app.form.browser.interfaces
        import zope.publisher.browser
        field = self.get_field()
        request = zope.publisher.browser.TestRequest()
        widget = zope.component.getMultiAdapter(
            (field, request),
            zope.app.form.browser.interfaces.IInputWidget)
        self.assertNotIsInstance(widget, ObjectSequenceWidget)

    def test_widget_should_render_source_query_view_and_no_url_input(self):
        import zeit.cms.content.interfaces
        import zope.component
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
        self.assertEllipsis('...<div>mock</div>...', result)
        self.assertNotEllipsis('...name="field..url"...', result)

    def test_widget_should_render_url_input_if_query_view_is_absent(self):
        widget = self.get_widget()
        result = widget()
        self.assertEllipsis('...name="field..url"...', result)

    def test_widget_should_render_add_view(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        field = self.get_field()
        content = TestContentType()
        content.ressort = u'Politik'
        field = field.bind(content)
        widget = self.get_widget(field)
        widget.add_type = zeit.cms.testcontenttype.interfaces.ITestContentType
        self.assert_ellipsis(
            '...<a target="_blank"'
            '...href="http://127.0.0.1/repository/politik/'
            '...zeit.cms.testcontenttype.Add...',
            widget())

    def test_accepted_types_is_escaped_for_javascript(self):
        field = self.get_field()
        widget = self.get_widget(field)
        with mock.patch.object(
                field.value_type.source, 'get_check_types') as types:
            types.return_value = [u'foo', 'bar']
            self.assertEqual('["type-foo", "type-bar"]', widget.accept_classes)

    def test_widget_detail_view_name_can_be_configured(self):
        field = self.get_field()
        widget = self.get_widget(field)
        widget.detail_view_name = '@@mydetails'
        self.assert_ellipsis("""...
            new zeit.cms.ObjectSequenceWidget(
                'field.', [...], '@@mydetails');...""", widget())


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
        s.waitForElementPresent("//input[@name='testwidget.0']")
        s.assertValue("//input[@name='testwidget.0']",
                      'http://xml.zeit.de/testcontent')

    def test_drop_should_increase_count(self):
        s = self.selenium
        s.assertValue("//input[@name='testwidget.count']", '0')
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue("//input[@name='testwidget.count']", '1')
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue("//input[@name='testwidget.count']", '2')

    def test_entering_uid_should_increase_count(self):
        s = self.selenium
        s.assertValue("//input[@name='testwidget.count']", '0')
        s.type("//input[@name='testwidget.url']",
               'http://xml.zeit.de/testcontent')
        s.waitForValue("//input[@name='testwidget.count']", '1')
        s.type("//input[@name='testwidget.url']",
               'http://xml.zeit.de/testcontent')
        s.waitForValue("//input[@name='testwidget.count']", '2')

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
        s.waitForElementPresent('css=a[rel=remove]')
        s.click('css=a[rel=remove]')
        s.waitForElementNotPresent('css=li.element')

    def test_remove_should_remove_hidden_field_with_unique_id(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForElementPresent("//input[@name='testwidget.0']")
        s.waitForElementPresent('css=a[rel=remove]')
        s.click('css=a[rel=remove]')
        s.waitForElementNotPresent("css=input[@name='testwidget.0']")

    def test_remove_should_decrease_count(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForValue("//input[@name='testwidget.count']", '1')
        s.waitForElementPresent('css=a[rel=remove]')
        s.click('css=a[rel=remove]')
        s.waitForValue("//input[@name='testwidget.count']", '0')

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
        s.assertValue("//input[@name='testwidget.0']",
                      'http://xml.zeit.de/testcontent')
        s.assertValue("//input[@name='testwidget.1']",
                      'http://xml.zeit.de/2007')
        s.dragAndDropToObject('css=li.element[index=0]',
                              'css=li.element[index=1]')
        s.assertValue("//input[@name='testwidget.0']",
                      'http://xml.zeit.de/2007')
        s.assertValue("//input[@name='testwidget.1']",
                      'http://xml.zeit.de/testcontent')


class ObjectWidgetMyDetails(zeit.cms.browser.view.Base):

    def __call__(self):
        return '<div class="mydetails" />'


def setup_mydetails():
    zope.configuration.xmlconfig.string("""\
<?xml version="1.0" encoding="UTF-8" ?>
<configure
  package="zeit.cms.browser.tests"
  xmlns:browser="http://namespaces.zope.org/browser">

  <include package="zope.browserpage" file="meta.zcml" />

  <browser:page
    for="zeit.cms.interfaces.ICMSContent"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="mydetails"
    class=".test_widget.ObjectWidgetMyDetails"
    permission="zope.View"
    />

</configure>
""")

def teardown_mydetails():
    zope.component.getSiteManager().unregisterAdapter(
        required=(zeit.cms.interfaces.ICMSContent,
                  zeit.cms.browser.interfaces.ICMSLayer),
        provided=zope.interface.Interface,
        name='mydetails')


class ObjectWidgetDetailViews(
    zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(ObjectWidgetDetailViews, self).setUp()
        setup_mydetails()

    def tearDown(self):
        teardown_mydetails()
        super(ObjectWidgetDetailViews, self).tearDown()

    def test_object_sequence_widgets_use_their_configured_views(self):
        self.open(
            '/@@/zeit.cms.javascript.base/tests/'
            'objectsequencewidget-detail-views.html')
        s = self.selenium
        s.assertElementNotPresent('css=div.supertitle')
        self.eval(
            "zeit.cms.test_widget.add('http://xml.zeit.de/testcontent');")
        s.waitForElementPresent('css=div.supertitle')
        s.assertElementNotPresent('css=div.mydetails')
        self.eval(
            "zeit.cms.test_widget2.add('http://xml.zeit.de/testcontent');")
        s.waitForElementPresent('css=div.mydetails')

    def test_drop_object_widgets_use_their_configured_views(self):
        self.open(
            '/@@/zeit.cms.javascript.base/tests/'
            'dropobjectwidget-detail-views.html')
        s = self.selenium
        s.assertElementNotPresent('css=div.supertitle')
        self.eval(
            "zeit.cms.test_widget.set('http://xml.zeit.de/testcontent');")
        s.waitForElementPresent('css=div.supertitle')
        s.assertElementNotPresent('css=div.mydetails')
        self.eval(
            "zeit.cms.test_widget2.set('http://xml.zeit.de/testcontent');")
        s.waitForElementPresent('css=div.mydetails')


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
        s.type('css=.autocomplete', 'a')
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

    def test_url_input_should_set_input_value(self):
        s = self.selenium
        s.type("//input[@name='testwidget.url']",
               'http://xml.zeit.de/testcontent')
        s.waitForValue('name=testwidget',
                       'http://xml.zeit.de/testcontent')

    def test_remove_should_clear_input_value(self):
        s = self.selenium
        s.dragAndDropToObject('id=drag', 'id=testwidget')
        s.waitForNotValue('name=testwidget', '')
        s.waitForElementPresent('css=#testwidget a')
        s.click('css=#testwidget a')
        s.waitForValue('name=testwidget', '')


class TestDropObjectWidgetAccept(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(TestDropObjectWidgetAccept, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/dropobjectwidget-accept.html')

    def start_drag(self, locator):
        s = self.selenium
        s.mouseDown(locator)
        s.mouseMoveAt(locator, '10,10')

    def test_accepted_class_should_make_dropzone_active(self):
        s = self.selenium
        self.start_drag('id=drag')
        s.assertElementPresent('css=.droppable-active')

    def test_not_accepted_class_should_not_make_dropzone_active(self):
        s = self.selenium
        self.start_drag('id=drag2')
        s.assertElementNotPresent('css=.droppable-active')


class TestDropObjectWidgetIntegration(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        import zope.security.management
        super(TestDropObjectWidgetIntegration, self).setUp()
        zope.security.management.endInteraction()

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

    def test_accepted_types_is_escaped_for_javascript(self):
        from zeit.cms.browser.widget import DropObjectWidget
        choice = self.get_choice()
        ANY = None
        widget = DropObjectWidget(choice, choice.source, ANY)
        with mock.patch.object(choice.source, 'get_check_types') as types:
            types.return_value = [u'foo', 'bar']
            self.assertEqual('["type-foo", "type-bar"]', widget.accept_classes)

    def test_widget_detail_view_name_can_be_configured(self):
        choice = self.get_choice()
        request = zope.publisher.browser.TestRequest()
        widget = zeit.cms.browser.widget.DropObjectWidget(
            choice, choice.source, request)
        widget.detail_view_name = '@@mydetails'
        self.assertEllipsis("""...new zeit.cms.DropObjectWidget(
                'field.', [...], '@@mydetails');...""", widget())

    def test_widget_has_url_input(self):
        choice = self.get_choice()
        request = zope.publisher.browser.TestRequest()
        widget = zeit.cms.browser.widget.DropObjectWidget(
            choice, choice.source, request)
        self.assertEllipsis('...name="field..url"...', widget())

    def test_widget_should_render_add_view(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        choice = self.get_choice()
        request = zope.publisher.browser.TestRequest()
        content = TestContentType()
        content.ressort = u'Politik'
        choice = choice.bind(content)
        widget = zeit.cms.browser.widget.DropObjectWidget(
            choice, choice.source, request)
        widget.add_type = zeit.cms.testcontenttype.interfaces.ITestContentType
        self.assertEllipsis(
            '...<a target="_blank"'
            '...href="http://127.0.0.1/repository/politik/'
            '...zeit.cms.testcontenttype.Add...',
            widget())


class DropObjectWidget(zeit.cms.testing.FunctionalTestCase):

    def test_setting_invalid_uniqueId_should_raise(self):
        context = mock.Mock()
        context.__name__ = 'foo'
        widget = zeit.cms.browser.widget.DropObjectWidget(
            context, mock.Mock(), mock.Mock())
        self.assertRaises(
            zope.formlib.interfaces.ConversionError,
            lambda: widget._toFieldValue('http://xml.zeit.de/nonexistent'))

    def test_setting_valid_uniqueId_returns_content_object(self):
        context = mock.Mock()
        context.__name__ = 'foo'
        widget = zeit.cms.browser.widget.DropObjectWidget(
            context, mock.Mock(), mock.Mock())
        self.assertEqual(
            self.repository['testcontent'],
            widget._toFieldValue('http://xml.zeit.de/testcontent'))


class TestObjectSequenceDisplayWidget(unittest2.TestCase):

    def get_content(self):
        import zeit.cms.interfaces
        import zope.interface
        content = mock.Mock()
        zope.interface.alsoProvides(
            content, zeit.cms.interfaces.ICMSContent)
        return content

    def get_widget(self):
        context = mock.Mock()
        context.__name__ = 'name'
        return ObjectSequenceDisplayWidget(context, mock.Mock(), mock.Mock())

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
    zeit.cms.testing.FunctionalTestCase,
    zeit.cms.testing.BrowserAssertions):

    def setUp(self):
        import zope.security.management
        super(TestObjectSequenceDisplayWidgetIntegration, self).setUp()
        zope.security.management.endInteraction()
        setup_mydetails()

    def tearDown(self):
        teardown_mydetails()
        super(TestObjectSequenceDisplayWidgetIntegration, self).tearDown()

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

    def test_should_use_configured_detail_views(self):
        widget = self.get_widget()
        widget.detail_view_name = '@@mydetails'
        zeit.cms.testing.set_site(self.getRootFolder())
        content = self.get_content()
        widget._data = (content,)
        with zeit.cms.testing.interaction():
            self.assert_ellipsis(
                '...<div...id="field."...mydetails...', widget())


class RestructuredTextWidgetTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(RestructuredTextWidgetTest, self).setUp()
        from zeit.cms.browser.widget import RestructuredTextWidget
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.IViviSkin)
        field = zope.schema.Text()
        field.__name__ = 'foo'
        self.widget = RestructuredTextWidget(field, request)

    def test_renders_both_textarea_and_preview(self):
        self.widget.setRenderedValue('foo bar baz')
        self.assertEllipsis("""\
<textarea...id="field.foo"...>foo bar baz</textarea>...
<div...id="field.foo.preview"...><p>foo bar baz</p> </div>
<script...new zeit.cms.RestructuredTextWidget('field.foo'); </script>""",
                            self.widget())

    def test_text_starting_with_http_is_rendered_as_link(self):
        self.widget.setRenderedValue('foo http://example.com bar')
        self.assertEllipsis(
            '...<a...href="http://example.com">http://example.com</a>...',
            self.widget())


class RestructuredTextWidgetJavascriptTest(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(RestructuredTextWidgetJavascriptTest, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/restructuredtext.html')

    def test_clicking_preview_div_shows_textarea(self):
        s = self.selenium
        s.assertVisible('id=testwidget.preview')
        s.waitForNotVisible('id=testwidget')
        s.click('id=testwidget.preview')
        s.waitForVisible('id=testwidget')
        s.assertNotVisible('id=testwidget.preview')

    def test_clicking_on_a_link_opens_it(self):
        s = self.selenium
        s.click('link=my link')
        s.selectWindow(s.getAllWindowNames()[-1])
        s.assertNotLocation('*/restructuredtext.html')
        s.close()
        s.selectWindow()
        s.assertNotVisible('id=testwidget')

    def test_empty_preview_can_be_clicked(self):
        s = self.selenium
        self.eval('window.jQuery("#testwidget\\\\.preview").text("")')
        s.click('css=.field')
        s.waitForVisible('id=testwidget')
        s.assertNotVisible('id=testwidget.preview')
