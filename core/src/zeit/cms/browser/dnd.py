import zope.component

import zeit.cms.interfaces


class DragPane:
    def __call__(self, uniqueId):
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        view = zope.component.getMultiAdapter((content, self.request), name='drag-pane.html')
        return view()
