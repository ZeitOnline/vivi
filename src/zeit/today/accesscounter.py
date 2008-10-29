# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.interfaces


class AccessCounter(object):

    zope.interface.implements(zeit.cms.content.interfaces.IAccessCounter)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context

    @property
    def hits(self):
        storage = zope.component.getUtility(
            zeit.today.interfaces.ICountStorage)
        return storage.get_count(self.context.uniqueId)

    @property
    def total_hits(self):
        lifetime = zeit.today.interfaces.ILifeTimeCounter(self.context, None)
        if lifetime is None:
            return None
        if not lifetime.total_hits:
            return None

        # The lifetime total hits do not contain today's hits, but we want to
        # take today's hits into account.
        today = self.hits
        if today is None:
            today = 0

        return lifetime.total_hits + today
