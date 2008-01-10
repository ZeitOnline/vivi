# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.content.interfaces


class CMSContentSource(object):

    zope.interface.implements(zeit.cms.content.interfaces.ICMSContentSource)

    name = 'all-types'
    check_interfaces = zeit.cms.interfaces.ICMSContentType

    def __contains__(self, value):
        if not self.verify_interface(value):
            return False

        # Interface is correct, make sure the object actually is in the
        # repository
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        try:
            repository.getContent(value.uniqueId)
        except KeyError:
            return False

        return True

    def verify_interface(self, value):
        for name, interface in zope.component.getUtilitiesFor(
            self.check_interfaces):
            if interface.providedBy(value):
                return True
        return False


cmsContentSource = CMSContentSource()


class FolderSource(CMSContentSource):

    name = 'folders'

    def verify_interface(self, value):
        return zeit.cms.repository.interfaces.IFolder.providedBy(value)


folderSource = FolderSource()
