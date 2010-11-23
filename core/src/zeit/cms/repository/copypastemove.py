# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zope.component
import zope.container.interfaces
import zope.copypastemove
import zope.lifecycleevent



class CMSObjectMover(zope.copypastemove.ObjectMover):
    """Objectmover for ICMSContent."""

    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)

    def moveTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        chooser = zope.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)
        target[new_name] = obj
        new = target[new_name]
        return new_name


class CMSObjectCopier(zope.copypastemove.ObjectCopier):

    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)

    def copyTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        chooser = zope.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        new = repository.getCopyOf(obj.uniqueId)
        del new.__parent__
        del new.__name__
        target[new_name] = new  # This actually copies.
        new = target[new_name]
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(new, obj))
        return new_name
