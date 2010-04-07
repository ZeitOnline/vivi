# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zope.component


class DragPane(object):

    def __call__(self, uniqueId):
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        view = zope.component.getMultiAdapter(
            (content, self.request), name='drag-pane.html');
        return view()
