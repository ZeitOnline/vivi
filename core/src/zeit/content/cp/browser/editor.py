# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.viewlet.interfaces
from zeit.content.cp.i18n import MessageFactory as _


class Editor(object):

    title = _('Edit center page')


class Area(object):

    def list_boxes(self):
        result = []
        for box in self.context.values():
            viewlets = zope.component.getMultiAdapter(
                (box, self.request, self),
                zope.viewlet.interfaces.IViewletManager,
                name='zeit.content.cp.box-content')
            viewlets.update()
            css_class = ('box', 'type-' + box.type)
            result.append(dict(
                css_class=' '.join(css_class),
                contents=viewlets.render()))
        return result
