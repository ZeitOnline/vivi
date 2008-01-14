# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.content.gallery.interfaces
import zeit.content.gallery.gallery


class GalleryFormBase(object):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.gallery.interfaces.IGalleryMetadata,
            omit_readonly=False))

    field_groups = zeit.cms.browser.form.metadataFieldGroups

class AddGallery(GalleryFormBase, zeit.cms.browser.form.AddForm):

    title = _("Add gallery")
    factory = zeit.content.gallery.gallery.Gallery


class EditGallery(GalleryFormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit Gallery")
    form_fields = GalleryFormBase.form_fields.omit('__name__')


class DisplayGallery(GalleryFormBase, zeit.cms.browser.form.DisplayForm):

    title = _("Gallery")


class DisplayImageWidget(zope.app.form.browser.widget.DisplayWidget):

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        image = zope.component.getMultiAdapter(
            (content, self.request), name='index.html')
        return image.tag()

    def hasInput(self):
        return False


class EditEntry(zeit.cms.browser.form.EditForm):

    title = _("Edit gallery entry")
    form_fields = zope.formlib.form.Fields(
        zeit.content.gallery.interfaces.IGalleryEntry).omit('thumbnail')
    form_fields['image'].custom_widget = DisplayImageWidget

    redirect_to_parent_after_edit = True
    redirect_to_view = 'overview.html'

    field_groups = (
        gocept.form.grouped.RemainingFields(
            title=u'', css_class='full-width wide-widgets'),
    )
