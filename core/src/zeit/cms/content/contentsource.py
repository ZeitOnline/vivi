# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.content._bootstrapinterfaces


class CMSContentSource(object):
    """A source for all cms content."""

    zope.interface.implements(
        zeit.cms.content._bootstrapinterfaces.INamedCMSContentSource)

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
    """A source containing folders."""

    name = 'folders'

    def verify_interface(self, value):
        return zeit.cms.repository.interfaces.IFolder.providedBy(value)


folderSource = FolderSource()


class ChoicePropertyWithCMSContentSource(object):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        zeit.cms.content._bootstrapinterfaces.ICMSContentSource)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        if not value:
            return None
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        try:
            content = repository.getContent(value)
        except (KeyError, ValueError):
            return
        if content in self.source:
            return content

    def toProperty(self, value):
        return value.uniqueId
