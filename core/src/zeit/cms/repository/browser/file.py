import os.path

import gocept.form.grouped
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.textwidgets
import zope.interface
import zope.security.proxy

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.repository.file
import zeit.cms.repository.interfaces


@zope.component.adapter(zeit.cms.repository.interfaces.IFile, zeit.cms.browser.interfaces.ICMSLayer)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class FileListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    author = title = subtitle = ressort = volume = page = year = searchableText = None


class FileView:
    title = _('View file')


class IFileEditSchema(zope.interface.Interface):
    __name__ = zope.schema.TextLine(title=_('File name'), required=False)

    blob = zope.schema.Object(zope.interface.Interface, title=_('Upload new file'))


class BlobWidget(zope.formlib.textwidgets.FileWidget):
    def _toFieldValue(self, input):
        if input is None or input == '':
            return self.context.missing_value
        try:
            input.seek
            input.read
        except AttributeError as e:
            raise zope.formlib.interfaces.ConversionError(_('Form input is not a file object'), e)
        else:
            if getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value


BUFFER_SIZE = 10240


def update_file(file, data):
    target = zope.security.proxy.removeSecurityProxy(file.open('w'))
    s = data.read(BUFFER_SIZE)
    while s:
        target.write(s)
        s = data.read(BUFFER_SIZE)
    data.close()
    target.close()


class FormBase:
    form_fields = zope.formlib.form.FormFields(IFileEditSchema)
    form_fields['blob'].custom_widget = BlobWidget

    def update_file(self, file, data):
        return update_file(file, data)


class AddForm(FormBase, zeit.cms.browser.form.AddForm):
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


class EditForm(FormBase, zeit.cms.browser.form.FormBase, gocept.form.grouped.Form):
    form_fields = FormBase.form_fields.omit('__name__')
    title = _('Edit file')
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), 'file_edit.pt')
    )

    @zope.formlib.form.action(_('Apply'))
    def handle_apply(self, action, data):
        self.update_file(self.context, data['blob'])
        self.send_message(_('Your changes have been saved.'))
