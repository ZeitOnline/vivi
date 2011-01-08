# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""File views."""

import os.path

import ZODB.interfaces
import gocept.form.grouped
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.interface
import zope.security.proxy

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
from zeit.cms.i18n import MessageFactory as _


class FileListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.component.adapts(
        zeit.cms.repository.interfaces.IFile,
        zeit.cms.browser.interfaces.ICMSLayer)
    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)

    author = title = subtitle = byline = ressort = volume = page = year = \
            searchableText = None


class FileView(object):

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
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError(_('Form input is not a file object'), e)
        else:
            if getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value

class FormBase(object):

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

    def create(self, data):
        file = zeit.cms.repository.file.LocalFile()
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
