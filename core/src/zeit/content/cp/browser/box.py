# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component




class Add(object):

    def __call__(self, type):
        factory = zope.component.getAdapter(
            self.context, zeit.content.cp.interfaces.IBoxFactory,
            name=type)
        factory()


class PlaceHolderEdit(object):

    def list_box_types(self):
        result = []
        for name, adapter in zope.component.getAdapters(
            (self.context.__parent__,),
            zeit.content.cp.interfaces.IBoxFactory):
            if adapter.title is None:
                continue
            result.append(dict(
                type=name,
                title=adapter.title))
        return result


class PlaceHolderSwitchType(object):

    def __call__(self, type):
        # XXX keep order
        factory = zope.component.getAdapter(
            self.context.__parent__, zeit.content.cp.interfaces.IBoxFactory,
            name=type)
        factory()
        del self.context.__parent__[self.context.__name__]
