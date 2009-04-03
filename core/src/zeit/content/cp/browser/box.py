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


class Delete(object):

    def __call__(self, key):
        del self.context[key]


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


class SwitchType(object):

    def __init__(self, parent, toswitch, request):
        self.parent = parent
        self.toswitch = toswitch
        self.request = request

    def __call__(self, type):
        order = list(self.parent.keys())
        index = order.index(self.toswitch.__name__)
        del self.parent[self.toswitch.__name__]
        factory = zope.component.getAdapter(
            self.parent, zeit.content.cp.interfaces.IBoxFactory, name=type)
        created = factory()
        order[index] = created.__name__
        self.parent.updateOrder(order)
        return created



class PlaceHolderSwitchType(zeit.cms.browser.view.Base):

    def __call__(self, type):
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request),
            name='type-switcher')
        return self.url(switcher(type))


class DeleteFromTeaserBar(zeit.cms.browser.view.Base):

    def __call__(self, key):
        switcher = zope.component.getMultiAdapter(
            (self.context, self.context[key], self.request),
            name='type-switcher')
        return self.url(switcher('placeholder'))
