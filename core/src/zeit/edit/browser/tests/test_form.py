from unittest.mock import Mock

import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema

import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.edit.browser.form
import zeit.edit.browser.view
import zeit.edit.testing


class IExample(zope.interface.Interface):
    foo = zope.schema.TextLine(title='foo')


class WidgetCSSMixin(zeit.cms.testing.ZeitCmsTestCase):
    # XXX This test should be moved to zeit.cms.browser, but it seems nearly
    # impossible to instantiate an EditForm, so we punt on this for now;
    # InlineForms are friendlier (since they don't pull in the
    # main_template.pt)

    def render_form(self, form_class):
        ANY_CONTEXT = Mock()
        zope.interface.alsoProvides(ANY_CONTEXT, IExample)
        request = zope.publisher.browser.TestRequest()
        form = form_class(ANY_CONTEXT, request)
        return form()

    def test_css_class_on_widget_is_rendered_to_html(self):
        class ExampleForm(zeit.edit.browser.form.InlineForm):
            form_fields = zope.formlib.form.FormFields(IExample)
            legend = 'Legend'

            def setUpWidgets(self):
                super().setUpWidgets()
                self.widgets['foo'].vivi_css_class = 'barbaz qux'

        self.assertEllipsis(
            """\
...<div class="field fieldname-foo required fieldtype-text barbaz qux">
...<div class="label">...""",
            self.render_form(ExampleForm),
        )

    def test_widget_without_css_class_does_not_break(self):
        class ExampleForm(zeit.edit.browser.form.InlineForm):
            form_fields = zope.formlib.form.FormFields(IExample)
            legend = 'Legend'

        self.assertEllipsis(
            """\
...<div class="field fieldname-foo required fieldtype-text">
...<div class="label">...""",
            self.render_form(ExampleForm),
        )


class FoldableFormGroup(zeit.edit.testing.FunctionalTestCase):
    def render(self, in_workingcopy, folded_workingcopy=False, folded_repository=False):
        class ExampleForm(zeit.edit.browser.form.FoldableFormGroup):
            title = 'Example'

        if folded_workingcopy is not None:
            ExampleForm.folded_workingcopy = folded_workingcopy
        if folded_repository is not None:
            ExampleForm.folded_repository = folded_repository

        context = Mock()
        if in_workingcopy:
            zope.interface.alsoProvides(context, zeit.cms.checkout.interfaces.ILocalContent)
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(request, zeit.cms.browser.interfaces.ICMSLayer)
        form = ExampleForm(context, request, Mock(), Mock())
        return form()

    def test_setting_folded_workingcopy_renders_css_class(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=True, folded_workingcopy=True)
        )
        self.assertNotIn(
            '...folded...',
            self.render(in_workingcopy=False, folded_workingcopy=True, folded_repository=False),
        )

    def test_setting_folded_repository_renders_css_class(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=False, folded_repository=True)
        )
        self.assertNotIn('folded', self.render(in_workingcopy=True, folded_repository=True))

    def test_default_for_workingcopy_is_folded(self):
        self.assertEllipsis(
            '...folded...',
            self.render(in_workingcopy=True, folded_workingcopy=None, folded_repository=None),
        )

    def test_default_for_repository_is_folded(self):
        self.assertEllipsis(
            '...folded...',
            self.render(in_workingcopy=False, folded_workingcopy=None, folded_repository=None),
        )


class InlineFormTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_should_not_create_spurious_None_values(self):
        request = zope.publisher.browser.TestRequest(form={'edit.actions.apply': 'clicked'})
        form = InlineEditForm(self.repository['testcontent'], request)
        self.assertEllipsis('...value=""...', form())


class InlineEditForm(zeit.edit.browser.form.InlineForm):
    legend = ''
    prefix = 'edit'
    form_fields = zope.formlib.form.FormFields(zeit.cms.content.interfaces.ICommonMetadata).select(
        'supertitle', 'subtitle'
    )


class LightboxEditForm(zeit.edit.browser.view.EditBox):
    form_fields = zope.formlib.form.FormFields(zeit.cms.content.interfaces.ICommonMetadata).select(
        'supertitle', 'subtitle'
    )


class InlineFormAutoSaveTest(zeit.edit.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        with zeit.cms.testing.site(None):
            zope.configuration.xmlconfig.string(
                """\
<?xml version="1.0" encoding="UTF-8" ?>
<configure
  package="zeit.edit.browser.tests"
  xmlns:browser="http://namespaces.zope.org/browser">

  <include package="zope.browserpage" file="meta.zcml" />

  <browser:page
    for="zeit.cms.content.interfaces.ICommonMetadata"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="edit-inline.html"
    class=".test_form.InlineEditForm"
    permission="zeit.EditContent"
    />

  <browser:page
    for="zeit.cms.content.interfaces.ICommonMetadata"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="edit-lightbox.html"
    class=".test_form.LightboxEditForm"
    permission="zeit.EditContent"
    />

  <browser:page
    for="zeit.cms.content.interfaces.ICommonMetadata"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="inlineform"
    template="inlineform.pt"
    permission="zeit.EditContent"
    />

  <browser:page
    for="zeit.cms.content.interfaces.ICommonMetadata"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="inlineform-nested"
    template="inlineform-nested.pt"
    permission="zeit.EditContent"
    />

  <browser:page
    for="zeit.cms.content.interfaces.ICommonMetadata"
    layer="zeit.cms.browser.interfaces.ICMSLayer"
    name="inlineform-lightbox"
    template="inlineform-lightbox.pt"
    permission="zeit.EditContent"
    />

</configure>
"""
            )

    def tearDown(self):
        # XXX plone.testing.zca.pushGlobalRegistry() doesn't work,
        # the view is not found.
        with zeit.cms.testing.site(None):
            zope.component.getSiteManager().unregisterAdapter(
                required=(
                    zeit.cms.content.interfaces.ICommonMetadata,
                    zeit.cms.browser.interfaces.ICMSLayer,
                ),
                provided=zope.interface.Interface,
                name='autosave-edit',
            )
        super().tearDown()

    def test_submits_form_on_focusout(self):
        s = self.selenium
        self.open('/repository/testcontent/@@checkout')
        # XXX @@checkout?came_from=@@autosave-edit does not work
        self.open('/workingcopy/zope.user/testcontent/@@inlineform')

        input = 'edit.subtitle'
        s.waitForElementPresent(input)
        s.type(input, 'asdf')
        s.click('id=header')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.refresh()
        s.waitForElementPresent(input)
        s.assertValue(input, 'asdf')

    def test_nested_inlineform_only_submits_inner_form(self):
        s = self.selenium
        self.open('/repository/testcontent/@@checkout')
        self.open('/workingcopy/zope.user/testcontent/@@inlineform-nested')

        input = 'edit.subtitle'
        s.waitForElementPresent(input)

        self.execute('zeit.cms.InlineForm.submitted = 0;')
        self.execute(
            """zeit.cms.InlineForm.prototype.submit = function() {
            zeit.cms.InlineForm.submitted += 1; }"""
        )

        s.type(input, 'asdf')
        s.click('id=header')
        self.assertEqual(1, self.eval('zeit.cms.InlineForm.submitted'))

    def test_subpageform_in_lightbox_submits_correctly(self):
        s = self.selenium
        self.open('/repository/testcontent/@@checkout')
        self.open('/workingcopy/zope.user/testcontent/@@inlineform-lightbox')
        input = 'form.subtitle'
        s.waitForElementPresent(input)
        s.click('id=form.actions.apply')
        s.waitForElementNotPresent(input)
