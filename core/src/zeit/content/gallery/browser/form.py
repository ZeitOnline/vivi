# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.wysiwyg.interfaces
import zope.app.appsetup.interfaces
import zope.formlib.form

base = zeit.cms.content.browser.form.CommonMetadataFormBase

class GalleryFormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.content.gallery.interfaces.IGalleryMetadata)
        + zope.formlib.form.FormFields(
            zeit.content.gallery.interfaces.IMaxLengthHTMLContent))
    
    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'subtitle',
         'teaserTitle', 'teaserText', 'html',),
        css_class='wide-widgets column-left')

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class='column-right'),
        base.option_fields,
        )
    

class AddGallery(GalleryFormBase,
                 zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _("Add gallery")
    factory = zeit.content.gallery.gallery.Gallery
    next_view = 'overview.html'
    form_fields = GalleryFormBase.form_fields.omit(
        'automaticMetadataUpdateDisabled')


class EditGallery(GalleryFormBase,
                  zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _("Edit gallery")


class DisplayGallery(GalleryFormBase,
                     zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View gallery metadata")


class DisplayImageWidget(zope.app.form.browser.widget.DisplayWidget):

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        image = zope.component.getMultiAdapter(
            (content, self.request), name='view.html')
        return image.tag()

    def hasInput(self):
        return False


class EditEntry(zeit.cms.browser.form.EditForm):

    title = _("Edit gallery entry")
    form_fields = zope.formlib.form.FormFields(
        zeit.content.gallery.interfaces.IGalleryEntry).omit(
        'thumbnail', 'text')
    form_fields['image'].custom_widget = DisplayImageWidget

    redirect_to_parent_after_edit = True
    redirect_to_view = 'overview.html'

    field_groups = (
        gocept.form.grouped.Fields(
            title=u'',
            fields=('image', 'layout', 'caption', 'title', 'html'),
            css_class='full-width wide-widgets'),
    )

    def setUpWidgets(self):
        # XXX backwards compatibility only, should probably be removed at some
        # point (see #8858)
        if self.context.text is not None and self.context.text.countchildren():
            self.form_fields += zope.formlib.form.FormFields(
                zeit.wysiwyg.interfaces.IHTMLContent)
        super(EditEntry, self).setUpWidgets()
