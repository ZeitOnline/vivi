# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
import zeit.cms.content.add
import zope.formlib.form
import zope.session.interfaces


class Form(zope.formlib.form.SubPageForm):

    template = ViewPageTemplateFile('form.pt')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.IContentAdder).omit('year', 'month')
    prefix = 'sidebar.form'

    next_url = None

    def setUpWidgets(self, ignore_request=False):
        session = zope.session.interfaces.ISession(self.request).get(
            'zeit.addcentral', {})
        self.widgets = zope.formlib.form.setUpDataWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=session, for_display=False,
            ignore_request=ignore_request)

    @zope.formlib.form.action(_('Add'))
    def add(self, action, data):
        adder = zeit.cms.content.add.ContentAdder(self.request, **data)
        self.next_url = adder()
        zope.session.interfaces.ISession(
            self.request)['zeit.addcentral'].update(data)

    def nextURL(self):
        return self.next_url
