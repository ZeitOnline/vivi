# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.copypastemove.interfaces
import zope.interface

import zope.app.container.interfaces

import zeit.cms.repository.interfaces


class ObjectCopier(object):

    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)
    zope.interface.implements(zope.copypastemove.interfaces.IObjectCopier)

    def __init__(self, context):
        self.context = self.__parent__ = context

    def copyTo(self, target, new_name=None):
        obj = self.context
        target = zeit.cms.repository.interfaces.ICopy(target)

        if new_name is None:
            new_name = obj.__name__

        chooser = zope.app.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        target.copy(obj, new_name)
        return new_name

