from zeit.cms.i18n import MessageFactory as _
from zeit.content.image.browser.interfaces import IMasterImageUploadSchema
from zeit.content.image.interfaces import INFOGRAPHIC_DISPLAY_TYPE
from zope.formlib.widget import CustomWidgetFactory
import gocept.form.grouped
import itertools
import re
import zc.table.column
import zeit.cms.browser.form
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.content.image.browser.form
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.ghost.ghost
import zope.app.appsetup.appsetup
import zope.formlib.form
import zope.publisher.interfaces


class FormBase(object):

    field_groups = zeit.content.image.browser.form.ImageFormBase.field_groups

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageGroup,
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IReferences).omit(
            'acquire_metadata', 'variants')


class AddForm(FormBase,
              zeit.cms.repository.browser.file.FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add image group')
    factory = zeit.content.image.imagegroup.ImageGroup
    checkout = False
    form_fields = (
        FormBase.form_fields.omit(
            'references', 'master_images', 'external_id') +
        zope.formlib.form.FormFields(IMasterImageUploadSchema))

    form_fields['master_image_blobs'].custom_widget = (
        CustomWidgetFactory(
            zope.formlib.sequencewidget.SequenceWidget,
            zeit.cms.repository.browser.file.BlobWidget))

    def create(self, data):
        # Must remove master_image_blobs from data before creating the images,
        # since `zeit.cms.browser.form.apply_changes_with_setattr` breaks on
        # fields that are not actually part of the interface.
        blobs = data.pop('master_image_blobs')

        # Create ImageGroup with remaining data.
        group = super(AddForm, self).create(data)

        # Create images from blobs. Skip missing blobs, i.e. None.
        self.images = [self.create_image(blob, data) for blob in blobs if blob]

        # Prefill `master_images` with uploaded images and configure viewport.
        # Viewports should be prefilled sequentially, i.e. primary master image
        # is configured with first viewport of source, secondary master image
        # with second viewport etc.
        viewports = zeit.content.image.interfaces.VIEWPORT_SOURCE(group)
        for image, viewport in itertools.izip(self.images, viewports):
            group.master_images += ((viewport, image.__name__),)

        return group

    def add(self, group):
        super(AddForm, self).add(group)
        group = self._created_object  # We need IRepositoryContent.

        # Add images to ImageGroup container.
        for image in self.images:
            if image is not None:
                super(AddForm, self).add(image, group)

        self._created_object = group  # Additional add() calls overwrote this.
        zeit.ghost.ghost.create_ghost(group)

    def create_image(self, blob, data):
        image = zeit.content.image.image.LocalImage()
        self.update_file(image, blob)
        name = zeit.cms.interfaces.normalize_filename(
            getattr(blob, 'filename', ''))
        zeit.cms.browser.form.apply_changes_with_setattr(
            image,
            self.form_fields.omit('__name__', 'display_type'), data)
        image.__name__ = name
        return image

    @property
    def next_view(self):
        if self._created_object.display_type == INFOGRAPHIC_DISPLAY_TYPE:
            return 'view.html'
        return 'variant.html'

    def setUpWidgets(self, *args, **kw):
        super(AddForm, self).setUpWidgets(*args, **kw)
        self.widgets['master_image_blobs'].addButtonLabel = _('Add motif')
        self.widgets['master_image_blobs'].subwidget.extra = 'accept="%s"' % (
            ','.join(zeit.content.image.interfaces.AVAILABLE_MIME_TYPES))
        self.widgets['copyrights'].vivi_css_class = 'fieldname-copyrights--add'


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit image group')
    form_fields = FormBase.form_fields.omit('__name__')

    def setUpWidgets(self, *args, **kw):
        super(EditForm, self).setUpWidgets(*args, **kw)
        self.widgets['master_images'].addButtonLabel = _(
            'Add viewport to master image mapping')
        self.widgets['copyrights'].vivi_css_class = (
            'fieldname-copyrights--edit')


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Image group metadata')

    def setUpWidgets(self, *args, **kw):
        super(DisplayForm, self).setUpWidgets(*args, **kw)
        self.widgets['copyrights'].vivi_css_class = (
            'fieldname-copyrights--display')


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

    def filter_content(self, obj):
        """Do not display thumbnail images."""
        prefix = zeit.content.image.imagegroup.Thumbnails.SOURCE_IMAGE_PREFIX
        if obj.__name__.startswith(prefix):
            return False
        return super(View, self).filter_content(obj)


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
                return self.context[name]

        return zeit.content.image.interfaces.IMasterImage(self.context)


class ThumbnailLarge(Thumbnail):

    first_choice = re.compile(r'.*-[5-9][0-9]+x\d+')
    view_name = 'preview'


class DefaultView(zeit.cms.browser.view.Base):
    # XXX zope.publisher.defaultview insists on abusing the ZCA adapter
    # registry to store plain strings instead of real adapters, so we cannot
    # perform the distinction there, since no adapter is called.

    def __call__(self):
        view = '@@variant.html'
        if self.context.display_type == INFOGRAPHIC_DISPLAY_TYPE:
            view = '@@view.html'
        self.request.response.redirect(self.url(self.context, view))
