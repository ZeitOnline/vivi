# Copyright (c) 2008 gocept gmbh & co. kg
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


class EditForm(zeit.cms.browser.form.FormBase,
               gocept.form.grouped.Form):

    title = _('Edit file')
    form_fields = zope.formlib.form.FormFields(IFileEditSchema)
    form_fields['blob'].custom_widget = BlobWidget
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), 'file_edit.pt'))

    BUFFER_SIZE = 10240

    @zope.formlib.form.action(_('Apply'))
    def handle_apply(self, action, data):
        upload = data['blob']
        target = zope.security.proxy.removeSecurityProxy(
            self.context.open('w'))
        s = upload.read(self.BUFFER_SIZE)
        while s:
            target.write(s)
            s = upload.read(self.BUFFER_SIZE)
        target.close()
        self.context.mimeType = upload.headers['content-type']
        self.send_message(_('Your changes have been saved.'))
