# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import re
import zc.table.column
import zeit.cms.browser.form
import zeit.cms.browser.listing
import zeit.content.image.browser.form
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zope.formlib.form
import zope.publisher.interfaces


class FormBase(object):

    field_groups = zeit.content.image.browser.form.ImageFormBase.field_groups

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageGroup,
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IReferences).omit('acquire_metadata')


class AddForm(FormBase,
              zeit.cms.repository.browser.file.FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add image group')
    factory = zeit.content.image.imagegroup.ImageGroup
    checkout = False
    form_fields = (
        FormBase.form_fields.omit('references', 'master_image') +
        zope.formlib.form.FormFields(
            zeit.content.image.browser.interfaces.IMasterImageUploadSchema))

    form_fields['blob'].custom_widget = (
        zeit.cms.repository.browser.file.BlobWidget)

    def create(self, data):
        self.image = self.create_image(data)
        group = super(AddForm, self).create(data)
        if self.image:
            group.master_image = self.image.__name__
        return group

    def add(self, group):
        super(AddForm, self).add(group)
        if self.image is not None:
            super(AddForm, self).add(self.image, group)
        self._created_object = group

    def create_image(self, data):
        image = zeit.content.image.image.LocalImage()
        blob = data.pop('blob')
        if blob is None:
            return
        self.update_file(image, blob)
        name = getattr(blob, 'filename', '')
        zeit.cms.browser.form.apply_changes_with_setattr(
            image,
            self.form_fields.omit('__name__'), data)
        image.__name__ = name
        return image


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit image group')
    form_fields = FormBase.form_fields.omit('__name__')


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Image group metadata')


class ImageColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        return item.context

    def cell_formatter(self, value, item, formatter):
        img = zope.component.getMultiAdapter(
            (value, formatter.request),
            name='preview').tag()
        master = ''
        if zeit.content.image.interfaces.IMasterImage.providedBy(value):
            master = '<div class="master-image">%s</div>' % (
                zope.i18n.translate(_('Master image'),
                                    context=formatter.request))
        return img + master


class View(zeit.cms.browser.listing.Listing):

    title = _('Image group')
    filter_interface = zeit.content.image.interfaces.IImage

    columns = (
        zeit.cms.browser.listing.LockedColumn(u'', name='locked'),
        zeit.cms.browser.listing.GetterColumn(
            title=_("File name"),
            # zc.table can't deal with spaces in colum names
            name='filename',
            getter=lambda i, f: i.__name__),
        zeit.cms.browser.listing.GetterColumn(
            title=_('Dimensions'),
            getter=lambda i, f: i.context.getImageSize(),
            cell_formatter=lambda v, i, f: 'x'.join(str(i) for i in v)),
        ImageColumn(title=_('Image')),
        zeit.cms.browser.listing.MetadataColumn(u'Metadaten', name='metadata'),
    )


class AddImage(zeit.content.image.browser.form.AddForm):

    checkout = False

    field_groups = (
        gocept.form.grouped.RemainingFields(_("Image data")),
    )

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.browser.interfaces.IFileEditSchema)
    form_fields['blob'].custom_widget = (
        zeit.cms.repository.browser.file.BlobWidget)

    def nextURL(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        return url()


class Metadata(object):

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)

    @property
    def images(self):
        if not zeit.content.image.interfaces.IRepositoryImageGroup.providedBy(
            self.context):
            return
        for obj in self.context.values():
            if zeit.content.image.interfaces.IImage.providedBy(obj):
                yield obj


class Thumbnail(object):

    first_choice = re.compile(r'.*-\d+x\d+')
    view_name = 'thumbnail'

    def __call__(self):
        return self.image_view()

    def tag(self):
        return self.image_view.tag()

    @property
    def image_view(self):
        view = zope.component.getMultiAdapter(
            (self._find_image(), self.request), name=self.view_name)
        return view

    def _find_image(self):
        if not self.context.keys():
            raise zope.publisher.interfaces.NotFound(
                self.context, self.__name__, self.request)
        for name in self.context.keys():
            if self.first_choice.match(name):
                break
        else:
            name = self.context.keys()[0]
        return self.context[name]


class ThumbnailLarge(Thumbnail):

    first_choice = re.compile(r'.*-[5-9][0-9]+x\d+')
    view_name = 'preview'
