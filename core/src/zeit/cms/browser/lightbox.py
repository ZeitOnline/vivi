from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.view
import zope.app.pagetemplate
import zope.formlib.form


class Form(
    zeit.cms.browser.view.Base, zeit.cms.browser.form.WidgetCSSMixin, zope.formlib.form.SubPageForm
):
    """A form in a lightbox that redirects after submit."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('lightbox.pt')
    title = _('Form')
    display_only = False
    form = zope.app.pagetemplate.ViewPageTemplateFile('subpageform.pt')

    def nextURL(self):
        return self.url(self.context, '@@view.html')

    def get_data(self):
        """Returns dictionary of data."""
        raise NotImplementedError('Implemented in subclasses.')

    def setUpWidgets(self, ignore_request=False):
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields,
            self.prefix,
            self.context,
            self.request,
            data=self.get_data(),
            for_display=self.display_only,
            ignore_request=ignore_request,
        )
        # XXX copy&paste from WidgetCSSMixin since we're skipping super()
        for widget in self.widgets:
            widget.field_css_class = self._assemble_css_classes.__get__(widget)
