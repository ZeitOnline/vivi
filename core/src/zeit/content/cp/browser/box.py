# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.content.cp.interfaces
import zope.component


class Add(zeit.cms.browser.view.Base):

    def __call__(self, type):
        factory = zope.component.getAdapter(
            self.context, zeit.content.cp.interfaces.IBoxFactory,
            name=type)
        created = factory()
        return self.url(created)


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


class PlaceHolderSwitchType(zeit.cms.browser.view.Base):

    def __call__(self, type):
        # XXX keep order
        factory = zope.component.getAdapter(
            self.context.__parent__, zeit.content.cp.interfaces.IBoxFactory,
            name=type)
        created = factory()
        del self.context.__parent__[self.context.__name__]
        return self.url(created)
