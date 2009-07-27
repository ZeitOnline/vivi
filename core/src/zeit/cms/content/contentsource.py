# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.content.interfaces


class CMSContentSource(object):
    """A source for all cms content."""

    zope.interface.implements(
        zeit.cms.content.interfaces.INamedCMSContentSource)

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

    def get_check_interfaces(self):
        check = []
        if isinstance(self.check_interfaces, tuple):
            check.extend(self.check_interfaces)
        else:
            assert issubclass(self.check_interfaces,
                              zope.interface.interfaces.IInterface)
            for name, interface in zope.component.getUtilitiesFor(
                self.check_interfaces):
                check.append(interface)
        return check

    def get_check_types(self):
        types = []
        for interface in self.get_check_interfaces():
            __traceback_info__ = (interface,)
            types.append(interface.getTaggedValue('zeit.cms.type'))
        return types

    def verify_interface(self, value):
        for interface in self.get_check_interfaces():
            if interface.providedBy(value):
                return True
        return False


cmsContentSource = CMSContentSource()


class FolderSource(CMSContentSource):
    """A source containing folders."""

    name = 'folders'
    check_interfaces = (
        zeit.cms.repository.interfaces.IFolder,)


folderSource = FolderSource()


class ChoicePropertyWithCMSContentSource(object):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        zeit.cms.content.interfaces.ICMSContentSource)

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
