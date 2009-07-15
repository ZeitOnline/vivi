# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import zope.app.appsetup.interfaces

import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.wysiwyg.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.content.gallery.interfaces
import zeit.content.gallery.gallery


class GalleryFormBase(object):

    form_fields =zope.formlib.form.FormFields(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate,
        zeit.content.gallery.interfaces.IGalleryMetadata)


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
    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.gallery.interfaces.IGalleryEntry).omit(
            'thumbnail', 'text') +
        zope.formlib.form.FormFields(
            zeit.wysiwyg.interfaces.IHTMLContent))
    form_fields['image'].custom_widget = DisplayImageWidget

    redirect_to_parent_after_edit = True
    redirect_to_view = 'overview.html'

    field_groups = (
        gocept.form.grouped.Fields(
            title=u'',
            fields=('image', 'layout', 'caption', 'title', 'html'),
            css_class='full-width wide-widgets'),
    )


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register_asset_interface(event):
    zeit.cms.content.browser.form.AssetBase.add_asset_interface(
        zeit.content.gallery.interfaces.IGalleryReference)
