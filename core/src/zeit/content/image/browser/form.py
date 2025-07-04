import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
from zeit.content.image.transform import ImageTransform
import zeit.cms.browser.form
import zeit.cms.config
import zeit.cms.repository.browser.file
import zeit.content.image.browser.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.edit.browser.form


class ImageFormBase(zeit.cms.repository.browser.file.FormBase):
    field_groups = (
        gocept.form.grouped.Fields(
            _('Image data'),
            ('__name__', 'references', 'display_type'),
            css_class='column-left image-form',
        ),
        gocept.form.grouped.RemainingFields(
            _('Texts'), css_class='column-right image-form wide-widgets'
        ),
        gocept.form.grouped.Fields(
            _('Image source'),
            ('blob', 'master_image_blobs', 'master_images', 'mdb_blob'),
            css_class='column-left image-form',
        ),
    )

    form_fields = zope.formlib.form.FormFields(zeit.content.image.interfaces.IImageMetadata).omit(
        'acquire_metadata', 'origin'
    )

    def __init__(self, *args, **kw):
        self.form_fields['blob'].custom_widget = zeit.cms.repository.browser.file.BlobWidget
        super().__init__(*args, **kw)

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['blob'].extra = 'accept="%s"' % (
            ','.join(zeit.content.image.interfaces.AVAILABLE_MIME_TYPES)
        )


class CreateImageMixin:
    def _reduceToMaxImageSize(self, image):
        self.max_size = int(zeit.cms.config.get('zeit.content.image', 'max-image-size', 4000))
        size = image.getImageSize()
        largest = max(size)
        if largest > self.max_size:
            self.send_message(
                _(
                    'Image was resized, ${size} exceeds ${max_size}',
                    mapping={'size': largest, 'max_size': self.max_size},
                )
            )
            if size.index(largest) == 0:
                resize = {'width': self.max_size}
            else:
                resize = {'height': self.max_size}
            image = ImageTransform(image).resize(**resize)
        return image

    def create_image(self, blob, name=None, image=None):
        if image is None:
            image = zeit.content.image.image.LocalImage()
        if name is None:
            name = getattr(blob, 'filename', '')
        zeit.cms.repository.browser.file.update_file(image, blob)
        image = self._reduceToMaxImageSize(image)
        if name:
            image.__name__ = zeit.cms.interfaces.normalize_filename(name)
        return image


class AddForm(ImageFormBase, zeit.cms.browser.form.AddForm, CreateImageMixin):
    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.browser.interfaces.IFileAddSchema
    ) + ImageFormBase.form_fields.omit('references', 'external_id')

    title = _('Add image')
    factory = zeit.content.image.image.LocalImage

    def create(self, data):
        image = self.create_image(data.pop('blob'), data.pop('__name__'), image=self.new_object)
        self.applyChanges(image, data)
        return image


class EditForm(ImageFormBase, zeit.cms.browser.form.EditForm):
    title = _('Edit image')
    form_fields = (
        zope.formlib.form.FormFields(zeit.content.image.browser.interfaces.IFileEditSchema).omit(
            '__name__'
        )
        + ImageFormBase.form_fields
    )

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        blob = data.pop('blob')
        if blob:
            self.update_file(self.context, blob)
        form_fields = self.form_fields
        self.form_fields = form_fields.omit('blob')
        super().handle_edit_action.success(data)
        self.form_fields = form_fields

    def _get_widgets(self, form_fields, ignore_request):
        blob = form_fields.get('blob')
        if blob:
            form_fields = form_fields.omit('blob')
        widgets = super()._get_widgets(form_fields, ignore_request)
        if blob:
            widgets += zope.formlib.form.setUpWidgets(
                [blob],
                self.prefix,
                self.context,
                self.request,
                adapters=self.adapters,
                ignore_request=ignore_request,
            )
        return widgets


class EditReference(zeit.edit.browser.form.InlineForm):
    legend = ''

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageReference,
        # support read-only mode, see
        # zeit.content.article.edit.browser.form.FormFields
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE,
    ).select('caption', 'title', 'alt')

    @property
    def prefix(self):
        return 'reference-details-%s' % self.context.target.uniqueId
