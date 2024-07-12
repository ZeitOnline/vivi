import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.push.browser.form
import zeit.wysiwyg.interfaces


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class GalleryFormBase(zeit.push.browser.form.SocialBase, zeit.push.browser.form.MobileBase):
    # XXX We should switch to explicit select.
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.interfaces.ICMSContent,
        zeit.content.image.interfaces.IImages,
        zeit.content.gallery.interfaces.IGalleryMetadata,
        zeit.wysiwyg.interfaces.IHTMLContent,
    )

    text_fields = gocept.form.grouped.Fields(
        _('Texts'),
        (
            'supertitle',
            'title',
            'subtitle',
            'teaserTitle',
            'teaserText',
            'image',
            'fill_color',
            'html',
        ),
        css_class='wide-widgets column-left',
    )

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(_('misc.'), css_class='column-right'),
        zeit.push.browser.form.SocialBase.social_fields,
        zeit.push.browser.form.MobileBase.mobile_fields,
        base.option_fields,
    )


class AddGallery(GalleryFormBase, zeit.cms.content.browser.form.CommonMetadataAddForm):
    title = _('Add gallery')
    factory = zeit.content.gallery.gallery.Gallery
    next_view = 'overview.html'


class EditGallery(GalleryFormBase, zeit.cms.content.browser.form.CommonMetadataEditForm):
    title = _('Edit gallery')


class DisplayGallery(GalleryFormBase, zeit.cms.content.browser.form.CommonMetadataDisplayForm):
    title = _('View gallery metadata')


class DisplayImageWidget(zope.app.form.browser.widget.DisplayWidget):
    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        image = zope.component.getMultiAdapter((content, self.request), name='preview')
        return image.tag()

    def hasInput(self):
        return False


class EditEntry(zeit.cms.browser.form.EditForm):
    title = _('Edit gallery entry')
    form_fields = zope.formlib.form.FormFields(zeit.content.gallery.interfaces.IGalleryEntry).omit(
        'thumbnail', 'text'
    )
    form_fields['image'].custom_widget = DisplayImageWidget

    redirect_to_parent_after_edit = True
    redirect_to_view = 'overview.html'

    field_groups = (
        gocept.form.grouped.Fields(
            title='',
            fields=('image', 'layout', 'caption', 'title', 'html'),
            css_class='full-width wide-widgets',
        ),
    )

    def setUpWidgets(self):
        # XXX backwards compatibility only, should probably be removed at some
        # point (see #8858)
        if self.context.text is not None and self.context.text.getchildren():
            self.form_fields += zope.formlib.form.FormFields(zeit.wysiwyg.interfaces.IHTMLContent)
        super().setUpWidgets()
