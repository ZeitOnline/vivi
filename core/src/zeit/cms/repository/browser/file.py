from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import os.path
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.repository.file
import zeit.cms.repository.interfaces
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.security.proxy


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFile,
    zeit.cms.browser.interfaces.ICMSLayer)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class FileListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    author = title = subtitle = byline = ressort = volume = page = year = \
        searchableText = None


class FileView:

    title = _('View file')


class IFileEditSchema(zope.interface.Interface):

    __name__ = zope.schema.TextLine(
        title=_('File name'),
        required=False)

    blob = zope.schema.Object(
        zope.interface.Interface,
        title=_('Upload new file'))


class BlobWidget(zope.app.form.browser.FileWidget):

    def _toFieldValue(self, input):
        if input is None or input == '':
            return self.context.missing_value
        try:
            input.seek
            input.read
        except AttributeError as e:
            raise zope.formlib.interfaces.ConversionError(
                _('Form input is not a file object'), e)
        else:
            if getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value


class FormBase:

    form_fields = zope.formlib.form.FormFields(IFileEditSchema)
    form_fields['blob'].custom_widget = BlobWidget

    BUFFER_SIZE = 10240

    def update_file(self, file, data):
        target = zope.security.proxy.removeSecurityProxy(
            file.open('w'))
        s = data.read(self.BUFFER_SIZE)
        while s:
            target.write(s)
            s = data.read(self.BUFFER_SIZE)
        target.close()
        file.mimeType = data.headers['content-type']


class AddForm(FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add file')
    factory = zeit.cms.repository.file.LocalFile

    def create(self, data):
        file = self.new_object
        self.update_file(file, data['blob'])
        name = data.get('__name__')
        if not name:
            name = getattr(data['blob'], 'filename', '')
        if name:
            file.__name__ = name
        return file


class EditForm(FormBase,
               zeit.cms.browser.form.FormBase,
               gocept.form.grouped.Form):

    form_fields = FormBase.form_fields.omit('__name__')
    title = _('Edit file')
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), 'file_edit.pt'))

    @zope.formlib.form.action(_('Apply'))
    def handle_apply(self, action, data):
        self.update_file(self.context, data['blob'])
        self.send_message(_('Your changes have been saved.'))
