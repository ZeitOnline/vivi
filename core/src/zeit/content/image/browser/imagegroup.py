# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zeit.cms.browser.form

import gocept.form.grouped
import zc.table.column

import zeit.cms.browser.listing
from zeit.cms.i18n import MessageFactory as _

import zeit.content.image.interfaces
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.content.image.browser.form


class FormBase(zeit.content.image.browser.form.ImageFormBase):
    # get image form base for the field groups

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImageGroup) +
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImageMetadata))



class AddForm(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add image group')
    factory = zeit.content.image.imagegroup.ImageGroup
    checkout = False


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit image group')
    form_fields = FormBase.form_fields.omit('__name__')


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Image group metadata')


class ImageColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        return item.context

    def cell_formatter(self, value, item, formatter):
        return zope.component.getMultiAdapter(
            (value, formatter.request),
            name='preview').tag()


class View(zeit.cms.browser.listing.Listing):

    title = _('Image group')

    columns = (
        zc.table.column.SelectionColumn(idgetter=lambda item: item.__name__),
        zeit.cms.browser.listing.LockedColumn(u'', name='locked'),
        zeit.cms.browser.listing.GetterColumn(
            title=_("File name"),
            getter=lambda i, f: i.__name__),
        zeit.cms.browser.listing.GetterColumn(
            title=_('Dimensions'),
            getter=lambda i, f: i.context.getImageSize(),
            cell_formatter=lambda v, i, f: 'x'.join(str(i) for i in v)),
        ImageColumn(title=_('Image')),
        zeit.cms.browser.listing.MetadataColumn(u'Metadaten', name='metadata'),
    )


class AddImage(zeit.content.image.browser.form.AddForm):

    title = _("Add image")
    factory = zeit.content.image.image.Image
    checkout = False

    field_groups = (
        gocept.form.grouped.RemainingFields(_("Image data")),
    )
    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImage).omit('contentType')

    def nextURL(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        return url()


class Metadata(object):

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)
