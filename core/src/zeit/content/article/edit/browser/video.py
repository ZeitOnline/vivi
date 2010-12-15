# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.edit.browser.view
import zope.cachedescriptors.property
import zope.lifecycleevent
import zope.security


class SetVideo(zeit.edit.browser.view.Action):
    """Drop content object on an image."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.video = content
        zope.lifecycleevent.modified(self.context)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))


class EditVideo(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IVideo)


class EditVideoAction(zeit.edit.browser.view.EditBoxAction):

    title = _('Edit')
    action = 'edit'


class View(zeit.content.article.edit.browser.reference.View):

    @zope.cachedescriptors.property.Lazy
    def writable(self):
        return zope.security.canWrite(self.context, 'video')

    @zope.cachedescriptors.property.Lazy
    def has_content(self):
        return (self.context.video is not None or
                self.context.video_2 is not None)

