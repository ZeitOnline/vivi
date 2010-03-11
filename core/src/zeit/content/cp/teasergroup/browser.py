# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.cp.teasergroup.interfaces
import zeit.content.cp.teasergroup.teasergroup
import zope.app.pagetemplate
import zope.event
import zope.formlib.form
import zope.lifecycleevent


class CreateTeaserGroup(zope.formlib.form.SubPageForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'create.pt')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup).select(
            'name', 'automatically_remove')
    close = False

    # XXX validate context len>0
    @zope.formlib.form.action(_('Create teaser group'))
    def create(self, action, data):
        group = zeit.content.cp.teasergroup.teasergroup.TeaserGroup()
        zope.formlib.form.applyData(group, self.form_fields, data)
        group.teasers = tuple(self.context)
        group.create()
        zope.event.notify(
            zope.lifecycleevent.ObjectCreatedEvent(group))
        self.close = True

    @property
    def form(self):
        return super(CreateTeaserGroup, self).template



class DisplayTeaserGroup(zeit.cms.browser.form.DisplayForm):

    title = _('Display teaser group')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup).select(
            'name', 'automatically_remove', 'teasers')
