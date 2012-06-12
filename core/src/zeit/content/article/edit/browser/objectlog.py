# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zope.viewlet.viewlet


class ObjectLog(zope.viewlet.viewlet.ViewletBase):

    @property
    def repository_content(self):
        return zeit.cms.interfaces.ICMSContent(self.context.uniqueId, None)
