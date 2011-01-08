# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


class PublicationStatus(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublicationStatus)

    def __init__(self, context):
        self.context = context

    @property
    def published(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context, None)
        if info is None:
            return None
        if not info.published:
            return 'not-published'
        times = zope.dublincore.interfaces.IDCTimes(self.context)
        if (not times.modified
            or not info.date_last_published
            or info.date_last_published > times.modified):
            return 'published'
        return 'published-with-changes'
