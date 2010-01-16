# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zope.component


class DragPane(object):

    def __call__(self, uniqueId):
        content = self.repository.getContent(uniqueId)
        view = zope.component.getMultiAdapter(
            (content, self.request), name='drag-pane.html');
        return view()

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
