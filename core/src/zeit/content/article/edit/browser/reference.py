# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.edit.browser.view
import zope.cachedescriptors.property
import zope.formlib.form
import zope.lifecycleevent
import zope.security


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
    undo_description = _('edit portraitbox')


class View(object):
    """View for reference blocks."""

    @zope.cachedescriptors.property.Lazy
    def writable(self):
        return zope.security.canWrite(self.context, 'references')

    @zope.cachedescriptors.property.Lazy
    def has_content(self):
        return self.context.references is not None

    @property
    def css_class(self):
        css_class = []
        if zeit.content.article.edit.interfaces.ILayoutable.providedBy(
            self.context):
            if self.context.layout:
                css_class.append(self.context.layout)
        if self.writable:
            css_class.append('action-content-droppable')
            if not self.has_content:
                css_class.append('landing-zone visible')
        return ' '.join(css_class)
