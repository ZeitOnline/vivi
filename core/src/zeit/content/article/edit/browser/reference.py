# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.edit.browser.view
import zope.formlib.form
import zope.lifecycleevent


class SetReference(zeit.edit.browser.view.Action):
    """Drop content object on an IReference."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.references= content
        zope.lifecycleevent.modified(self.context)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))


class EditPortraitbox(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IPortraitbox).omit('references')


class EditPortraitboxAction(zeit.edit.browser.view.EditBoxAction):

    title = _('Edit')
    action = 'edit-layout'
