# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.content.gallery.interfaces import IGallery
from zeit.content.image.interfaces import IImageGroup
import zeit.content.article.edit.interfaces
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class EditBase(zeit.edit.browser.form.InlineForm):

    interface = NotImplemented
    fields = ('references',)
    legend = None

    @property
    def form_fields(self):
        return zope.formlib.form.FormFields(
            self.interface).select(*self.fields)

    @property
    def prefix(self):
        return '%s.%s' % (self.__class__.__name__, self.context.__name__)

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(EditBase, self).__call__()


class EditImage(EditBase):

    interface = zeit.content.article.edit.interfaces.IImage
    fields = ('references', 'layout', 'custom_caption')
    undo_description = _('edit image block')

    def setUpWidgets(self, *args, **kw):
        super(EditImage, self).setUpWidgets(*args, **kw)
        self.widgets['references'].add_type = IImageGroup


class EditGallery(EditBase):

    interface = zeit.content.article.edit.interfaces.IGallery
    undo_description = _('edit gallery block')

    def setUpWidgets(self, *args, **kw):
        super(EditGallery, self).setUpWidgets(*args, **kw)
        self.widgets['references'].add_type = IGallery


class EditPortraitbox(EditBase):

    interface = zeit.content.article.edit.interfaces.IPortraitbox
    undo_description = _('edit portraitbox block')


class EditInfobox(EditBase):

    interface = zeit.content.article.edit.interfaces.IInfobox
    undo_description = _('edit infobox block')


class EditVideo(EditBase):

    interface = zeit.content.article.edit.interfaces.IVideo
    fields = ('video', 'video_2', 'layout')
    undo_description = _('edit video block')
