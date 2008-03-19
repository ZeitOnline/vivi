# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zope.app.pagetemplate

import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _


class Form(zeit.cms.browser.view.Base,
           zope.formlib.form.SubPageForm):
    """A form in a lightbox."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('lightbox.pt')
    title = _('Form')

    def nextURL(self):
        return self.url(self.context, '@@view.html')

    @property
    def form(self):
        return super(Form, self).template
