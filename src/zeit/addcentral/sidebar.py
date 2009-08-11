# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
import zc.resourcelibrary
import zeit.addcentral.add
import zeit.addcentral.interfaces
import zeit.cms.content.sources
import zope.formlib.form


class Sidebar(object):

    def __init__(self, *args, **kw):
        zc.resourcelibrary.need('zeit.cms.content.dropdown')
        super(Sidebar, self).__init__(*args, **kw)


class Form(zope.formlib.form.SubPageForm):

    template = ViewPageTemplateFile('form.pt')
    form_fields = zope.formlib.form.FormFields(
        zeit.addcentral.interfaces.IContentAdder).omit('year', 'month')

    next_url = None

    @zope.formlib.form.action(_('Add'))
    def add(self, action, data):
        adder = zeit.addcentral.add.ContentAdder(self.request, **data)
        self.next_url = adder()

    def nextURL(self):
        return self.next_url
