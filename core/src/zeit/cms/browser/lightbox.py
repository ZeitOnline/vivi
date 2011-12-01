# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.formlib.form

import zope.app.pagetemplate

import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _


class Form(zeit.cms.browser.view.Base,
           zope.formlib.form.SubPageForm):
    """A form in a lightbox that redirects after submit."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('lightbox.pt')
    title = _('Form')
    display_only = False

    def nextURL(self):
        return self.url(self.context, '@@view.html')

    def get_data(self):
        """Returns dictionary of data."""
        raise NotImplementedError("Implemented in subclasses.")

    def setUpWidgets(self, ignore_request=False):
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=self.get_data(), for_display=self.display_only,
            ignore_request=ignore_request)

    @property
    def form(self):
        return super(Form, self).template
