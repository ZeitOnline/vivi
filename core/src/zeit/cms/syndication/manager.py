# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.interface

import zope.app.locking.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces

import zeit.cms.syndication.interfaces


class SyndicationManager(object):
    """A syndicaiton manager for CMS content."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.ISyndicationManager)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    @property
    def targets(self):
        return self._target_mapping.values()

    @property
    def canSyndicate(self):
        if not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
            self.context):
            # Only syndicated checked in content.
            return False
        if self.lockable.locked():
            # Do not syndicate locked content.
            return False
        return True

    def syndicate(self, targets):
        for target in targets:
            if target.uniqueId not in self._target_mapping:
                raise ValueError("Cannot syndicate to %s" % target.uniqueId)
            target.insert(0, self.context)

        event = zeit.cms.syndication.interfaces.ContentSyndicatedEvent(
            self.context, targets)
        zope.event.notify(event)

        for target in targets:
            self.repository.addContent(target)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @zope.cachedescriptors.property.Lazy
    def _target_mapping(self):
        location = zope.component.getUtility(
            zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
        workingcopy = location.getWorkingcopy()
        targets = zeit.cms.syndication.interfaces.IMySyndicationTargets(
            workingcopy).targets
        result = {}
        for target in targets:
            result[target.uniqueId] = target
        return result

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context)
