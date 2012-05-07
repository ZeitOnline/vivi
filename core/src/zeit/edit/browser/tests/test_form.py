# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from mock import Mock
import zeit.cms.testing
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema


class IExample(zope.interface.Interface):

    foo = zope.schema.TextLine(title=u'foo')


class InlineForm(zeit.cms.testing.FunctionalTestCase):

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
...<div class="widget-outer fieldname-foo barbaz qux">
<div class="label">...""", self.render_form(ExampleForm))

    def test_widget_without_css_class_does_not_break(self):
        class ExampleForm(zeit.edit.browser.form.InlineForm):
            form_fields = zope.formlib.form.FormFields(IExample)
            legend = 'Legend'

        self.assertEllipsis("""\
...<div class="widget-outer fieldname-foo">
<div class="label">...""", self.render_form(ExampleForm))
