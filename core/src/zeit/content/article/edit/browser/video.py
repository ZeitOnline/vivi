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
    undo_description = _('set video')
    name = 'video'

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        setattr(self.context, self.name, content)
        zope.lifecycleevent.modified(self.context)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))


class SetVideo2(SetVideo):

    name = 'video_2'


class EditVideo(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IVideo).select(
            'video', 'video_2', 'layout')
    undo_description = _('edit video block')


class EditVideoAction(zeit.edit.browser.view.EditBoxAction):

    title = _('Edit')
    action = 'edit'


class View(zeit.content.article.edit.browser.reference.View):

    @zope.cachedescriptors.property.Lazy
    def writable(self):
        # works the same for video_2 since they come from the same schema
        return zope.security.canWrite(self.context, 'video')

    @property
    def css_class(self):
        css_class = []
        if self.context.layout:
            css_class.append(self.context.layout)
        if self.writable:
            css_class.append('action-content-droppable')
        return ' '.join(css_class)
