# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.content.article.edit.interfaces
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class EditVideo(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IVideo).select(
            'video', 'video_2', 'layout')
    undo_description = _('edit video block')

    @property
    def prefix(self):
        return 'video.{0}'.format(self.context.__name__)

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(EditVideo, self).__call__()
