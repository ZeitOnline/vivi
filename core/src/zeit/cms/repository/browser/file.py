# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""File views."""

import zope.component
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


class EditForm(zeit.cms.browser.view.Base):

    title = _('Edit file')

    BUFFER_SIZE = 10240

    def update(self):
        if 'form.actions.apply' not in self.request.form:
            return
        upload = self.request.form['form.upload']
        target = zope.security.proxy.removeSecurityProxy(
            self.context.open('w'))
        s = upload.read(self.BUFFER_SIZE)
        while s:
            target.write(s)
            s = upload.read(self.BUFFER_SIZE)
        target.close()
        self.context.mimeType = upload.headers['content-type']
        self.send_message(_('Your changes have been saved.'))
