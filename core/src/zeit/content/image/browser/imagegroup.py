from zeit.cms.i18n import MessageFactory as _
from zeit.content.image.browser.interfaces import IMasterImageUploadSchema
from zeit.content.image.browser.mdb import MDBImportWidget
from zeit.content.image.interfaces import INFOGRAPHIC_DISPLAY_TYPE
from zope.formlib.widget import CustomWidgetFactory
import gocept.form.grouped
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
import zeit.workflow.interfaces
import zope.app.appsetup.appsetup
import zope.formlib.form
import zope.publisher.interfaces


class FormBase:

    field_groups = zeit.content.image.browser.form.ImageFormBase.field_groups

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageGroup,
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IReferences).omit(
            'acquire_metadata', 'variants')


class AddForm(FormBase,
              zeit.cms.repository.browser.file.FormBase,
              zeit.cms.browser.form.AddForm,
              zeit.content.image.browser.form.Resize):

    title = _('Add image group')
    factory = zeit.content.image.imagegroup.ImageGroup
    checkout = False
    form_fields = (
        FormBase.form_fields.omit(
            'references', 'master_images', 'external_id') +
        zope.formlib.form.FormFields(IMasterImageUploadSchema) +
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.ITimeBasedPublishing).select(
                'release_period')
    )

    form_fields['master_image_blobs'].custom_widget = (
        CustomWidgetFactory(
            zope.formlib.sequencewidget.SequenceWidget,
            zeit.cms.repository.browser.file.BlobWidget))
    form_fields['mdb_blob'].custom_widget = MDBImportWidget

    field_groups = FormBase.field_groups + (
        gocept.form.grouped.Fields(
            _("Settings"), ('release_period',),
            css_class='column-left image-form'),)

    def __init__(self, *args, **kw):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.image')
        if not config.get('mdb-api-url'):
            self.form_fields = self.form_fields.omit('mdb_blob')
        self.max_size = config.get('max-image-size', 4000)
        super(AddForm, self).__init__(*args, **kw)

    def validate(self, action, data):
        # SequenceWidget._generateSequence() silently discards invalid entries,
        # which seems... totally wrong. But to change that we'd have to copy
        # the entire method (just to replace the call to hasValidInput with
        # hasInput), so we sneak in from another angle instead. However, when
        # e.g. later on rendering the form again, getInputValue() must not
        # raise InputError, so we carefully have to scope our monkey patch to
        # just the form's validate() phase. XXX Should we change SequenceWidget
        # in vivi generally (in spite of annoying copy&paste), not just here?
        def getWidgetAndValidate(self, i):
            child = original_get(i)
            child.original_input = child.hasValidInput
            child.hasValidInput = child.hasInput
            return child

        widget = self.widgets['master_image_blobs']
        original_get = widget._getWidget
        widget._getWidget = getWidgetAndValidate.__get__(widget)

        result = super(AddForm, self).validate(action, data)

        widget._getWidget = original_get
        for child in widget._widgets.values():
            child.hasValidInput = child.original_input

        return result

    def create(self, data):
        # Must remove master_image_blobs from data before creating the images,
        # since `zeit.cms.browser.form.apply_changes_with_setattr` breaks on
        # fields that are not actually part of the interface.
        blobs = data.pop('master_image_blobs', ()) + (
            data.pop('mdb_blob', None),)

        # Create ImageGroup with remaining data.
        group = super(AddForm, self).create(data)

        # Create images from blobs. Skip missing blobs, i.e. None.
        self.images = [self.create_image(blob, data) for blob in blobs if blob]

        # Prefill `master_images` with uploaded images and configure viewport.
        # Viewports should be prefilled sequentially, i.e. primary master image
        # is configured with first viewport of source, secondary master image
        # with second viewport etc.
        viewports = zeit.content.image.interfaces.VIEWPORT_SOURCE
        for image, viewport in zip(self.images, viewports):
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

    def createAndAdd(self, data):
        # XXX cannot set this until object is in repository, since it wants to
        # objectlog, which requires a uniqueId.
        release_period = data.pop('release_period')
        super(AddForm, self).createAndAdd(data)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self._created_object)
        info.release_period = release_period

    def create_image(self, blob, data):
        image = zeit.content.image.image.LocalImage()
        self.update_file(image, blob)
        image = self.reduceToMaxImageSize(image)
        name = getattr(blob, 'filename', '')
        if name:
            image.__name__ = zeit.cms.interfaces.normalize_filename(name)
        zeit.cms.browser.form.apply_changes_with_setattr(
            image,
            self.form_fields.omit('__name__', 'display_type'), data)
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
        self.widgets['copyright'].vivi_css_class = 'fieldname-copyright--add'


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit image group')
    form_fields = FormBase.form_fields.omit('__name__')

    def setUpWidgets(self, *args, **kw):
        super(EditForm, self).setUpWidgets(*args, **kw)
        self.widgets['master_images'].addButtonLabel = _(
            'Add viewport to master image mapping')
        self.widgets['copyright'].vivi_css_class = (
            'fieldname-copyright--edit')


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Image group metadata')

    def setUpWidgets(self, *args, **kw):
        super(DisplayForm, self).setUpWidgets(*args, **kw)
        self.widgets['copyright'].vivi_css_class = (
            'fieldname-copyright--display')


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
        zeit.cms.browser.listing.LockedColumn('', name='locked'),
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
        zeit.cms.browser.listing.MetadataColumn('Metadaten', name='metadata'),
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


class Metadata:

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


class Thumbnail:

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
