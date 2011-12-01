
# See also LICENSE.txt

import datetime

import gocept.form.grouped
import zope.app.appsetup.interfaces
import zope.formlib.form
import zope.i18nmessageid

import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.cms.repository.browser.file
import zeit.content.image.browser.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _


class ImageFormBase(zeit.cms.repository.browser.file.FormBase):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Image data"), (
                '__name__', 'blob', 'master_image', 'alignment', 'references'),
            css_class='column-left image-form'),
        gocept.form.grouped.RemainingFields(
            _("Texts"),
            css_class='column-right image-form wide-widgets'),
    )

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IReferences).omit('acquire_metadata')

    def __init__(self, *args, **kw):
        self.form_fields['blob'].custom_widget = (
            zeit.cms.repository.browser.file.BlobWidget)
        super(ImageFormBase, self).__init__(*args, **kw)


class AddForm(ImageFormBase, zeit.cms.browser.form.AddForm):

    form_fields = (zope.formlib.form.FormFields(
        zeit.content.image.browser.interfaces.IFileAddSchema)
                   + ImageFormBase.form_fields.omit('references'))

    title = _("Add image")

    def create(self, data):
        image = zeit.content.image.image.LocalImage()
        blob = data.pop('blob')
        self.update_file(image, blob)
        name = data.pop('__name__')
        if not name:
            name = getattr(blob, 'filename', '')
        if name:
            image.__name__ = name
        self.applyChanges(image, data)
        return image


class EditForm(ImageFormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit image")
    form_fields = (zope.formlib.form.FormFields(
        zeit.content.image.browser.interfaces.IFileEditSchema).omit('__name__')
                   + ImageFormBase.form_fields)

    def applyChanges(self, data):
        blob = data.pop('blob')
        if blob:
            self.update_file(self.context, blob)
        form_fields = self.form_fields
        self.form_fields = form_fields.omit('blob')
        super(EditForm, self).applyChanges(data)
        self.form_fields = form_fields

    def _get_widgets(self, form_fields, ignore_request):
        blob = form_fields.get('blob')
        if blob:
            form_fields = form_fields.omit('blob')
        widgets = super(EditForm, self)._get_widgets(form_fields,
                                                      ignore_request)
        if blob:
            widgets += zope.formlib.form.setUpWidgets(
                [blob], self.prefix, self.context, self.request,
                adapters=self.adapters, ignore_request=ignore_request)
        return widgets
