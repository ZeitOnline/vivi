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
