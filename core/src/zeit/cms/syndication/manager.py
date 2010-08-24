# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.interface

import zope.app.locking.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.workingcopy.interfaces

import zeit.cms.syndication.interfaces
from zeit.cms.i18n import MessageFactory as _


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
        return sorted(
            self._target_mapping.values(),
            key=lambda t: t.uniqueId)

    @property
    def canSyndicate(self):
        if not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
            self.context):
            # Only syndicated checked in content.
            return False
        if self.lockable is not None and self.lockable.locked():
            # Do not syndicate locked content.
            return False
        return True

    def syndicate(self, targets, **kw):
        targets = list(targets)
        for target in targets:
            if target.uniqueId not in self._target_mapping:
                raise ValueError("Cannot syndicate to %s" % target.uniqueId)

        checked_out = []
        for target in targets:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(target)
            try:
                checked_out.append(manager.checkout(temporary=True))
            except zeit.cms.checkout.interfaces.CheckinCheckoutError:
                for co in checked_out:
                    del co.__parent__[co.__name__]
                raise zeit.cms.syndication.interfaces.SyndicationError(
                    target.uniqueId)

        # Everything is checked out now. Syndicate.
        for target in checked_out:
            target.insert(0, self.context)
            if kw:
                metadata = target.getMetadata(self.context)
                for key, value in kw.items():
                    setattr(metadata, key, value)

        for target in checked_out:
            manager = zeit.cms.checkout.interfaces.ICheckinManager(target)
            manager.checkin()

        event = zeit.cms.syndication.interfaces.ContentSyndicatedEvent(
            self.context, targets)
        zope.event.notify(event)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @zope.cachedescriptors.property.Lazy
    def lockable(self):
        return zope.app.locking.interfaces.ILockable(self.context, None)

    @zope.cachedescriptors.property.Lazy
    def _target_mapping(self):
        location = zope.component.getUtility(
            zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
        workingcopy = location.getWorkingcopy()
        targets = zeit.cms.syndication.interfaces.IMySyndicationTargets(
            workingcopy)
        result = {}
        for target in targets:
            feed = zeit.cms.syndication.interfaces.IFeed(target, None)
            if feed is not None:
                result[target.uniqueId] = target
        return result
