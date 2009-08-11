# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.resourcelibrary
import zeit.addcentral.add
import zeit.addcentral.interfaces
import zeit.cms.content.browser.form
import zeit.cms.content.sources
import zope.cachedescriptors.property
import zope.formlib.form


class Form(zope.formlib.form.SubPageForm):

    field_groups = None
    form_fields = zope.formlib.form.FormFields(
        zeit.addcentral.interfaces.IContentAdder).omit('year', 'month')

    @property
    def template(self):
        zc.resourcelibrary.need('zeit.cms.content.dropdown')
        return super(Form, self).template

    @zope.formlib.form.action(_('Add'))
    def add(self, action, data):
        import pdb; pdb.set_trace();
