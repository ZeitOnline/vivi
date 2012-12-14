# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from mock import Mock
import zeit.cms.testing
import zeit.edit.browser.form
import zeit.edit.testing
import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema


class IExample(zope.interface.Interface):

    foo = zope.schema.TextLine(title=u'foo')


class InlineForm(zeit.cms.testing.FunctionalTestCase):

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
                super(ExampleForm, self).setUpWidgets()
                self.widgets['foo'].vivi_css_class = 'barbaz qux'

        self.assertEllipsis("""\
...<div class="field fieldname-foo required fieldtype-text barbaz qux">
<div class="label">...""", self.render_form(ExampleForm))

    def test_widget_without_css_class_does_not_break(self):
        class ExampleForm(zeit.edit.browser.form.InlineForm):
            form_fields = zope.formlib.form.FormFields(IExample)
            legend = 'Legend'

        self.assertEllipsis("""\
...<div class="field fieldname-foo required fieldtype-text">
<div class="label">...""", self.render_form(ExampleForm))


class FoldableFormGroup(zeit.edit.testing.FunctionalTestCase):

    def render(self, in_workingcopy,
               folded_workingcopy=False, folded_repository=False):
        class ExampleForm(zeit.edit.browser.form.FoldableFormGroup):
            title = 'Example'

        if folded_workingcopy is not None:
            ExampleForm.folded_workingcopy = folded_workingcopy
        if folded_repository is not None:
            ExampleForm.folded_repository = folded_repository

        context = Mock()
        if in_workingcopy:
            zope.interface.alsoProvides(
                context, zeit.cms.checkout.interfaces.ILocalContent)
        request = zope.publisher.browser.TestRequest()
        zope.interface.alsoProvides(
            request, zeit.cms.browser.interfaces.ICMSLayer)
        form = ExampleForm(context, request, Mock(), Mock())
        return form()

    def test_setting_folded_workingcopy_renders_css_class(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=True,
            folded_workingcopy=True))
        self.assertNotEllipsis(
            '...folded...', self.render(in_workingcopy=False,
            folded_workingcopy=True, folded_repository=False))

    def test_setting_folded_repository_renders_css_class(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=False,
            folded_repository=True))
        self.assertNotEllipsis(
            '...folded...', self.render(in_workingcopy=True,
            folded_repository=True))

    def test_default_for_workingcopy_is_folded(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=True,
            folded_workingcopy=None, folded_repository=None))

    def test_default_for_repository_is_folded(self):
        self.assertEllipsis(
            '...folded...', self.render(in_workingcopy=False,
            folded_workingcopy=None, folded_repository=None))
