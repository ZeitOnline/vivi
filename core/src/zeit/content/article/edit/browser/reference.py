import zope.formlib.form
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.interfaces import IAuthor
from zeit.content.gallery.interfaces import IGallery
from zeit.content.image.interfaces import INFOGRAPHIC_DISPLAY_TYPE, IImageGroup
import zeit.content.article.edit.interfaces
import zeit.edit.browser.form


class EditBase(zeit.edit.browser.form.InlineForm):
    interface = NotImplemented
    fields = ('references',)
    legend = None

    @property
    def form_fields(self):
        return zope.formlib.form.FormFields(self.interface).select(*self.fields)

    @property
    def prefix(self):
        return '%s.%s' % (self.__class__.__name__, self.context.__name__)

    def __call__(self):
        zope.interface.alsoProvides(self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()


class EditImage(EditBase):
    interface = zeit.content.article.edit.interfaces.IImage
    fields = ('references', 'display_mode', 'variant_name', 'animation')

    @property
    def form_fields(self):
        """Omit Variant for Infographics, since Friedbert will use Original"""
        form_fields = super().form_fields
        if (
            self.context.references
            and self.context.references.target
            and IImageGroup.providedBy(self.context.references.target)
            and self.context.references.target.display_type == INFOGRAPHIC_DISPLAY_TYPE
        ):
            return form_fields.omit('variant_name')
        return form_fields

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['references'].add_type = IImageGroup

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        result = super().handle_edit_action.success(data)
        # needs to happen afterwards, since setting self.context.references
        # might replace the XML node, thus taking the attribute away
        if self.context.references:
            self.context.set_manually = True
        else:
            self.context.set_manually = False
        return result


class EditGallery(EditBase):
    interface = zeit.content.article.edit.interfaces.IGallery

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['references'].add_type = IGallery


class EditPortraitbox(EditBase):
    interface = zeit.content.article.edit.interfaces.IPortraitbox
    fields = ('references', 'name', 'text')

    @property
    def form_fields(self):
        form_fields = super().form_fields
        form_fields['text'].custom_widget = zeit.cms.browser.widget.MarkdownWidget
        return form_fields


class EditInfobox(EditBase):
    interface = zeit.content.article.edit.interfaces.IInfobox
    fields = ('references', 'layout')


class EditVideo(EditBase):
    interface = zeit.content.article.edit.interfaces.IVideo
    fields = ('video', 'layout')


class EditAuthor(EditBase):
    interface = zeit.content.article.edit.interfaces.IAuthor

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['references'].add_type = IAuthor


class EditVolume(EditBase):
    interface = zeit.content.article.edit.interfaces.IVolume


class EditAudio(EditBase):
    interface = zeit.content.article.edit.interfaces.IAudio
