# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.lxml.interfaces
import itertools
import uuid
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.event
import zope.interface
import zeit.content.cp.blocks.block


class Container(UserDict.DictMixin,
                zeit.content.cp.blocks.block.Element,
                zope.container.contained.Contained):

    zope.interface.implements(zeit.content.cp.interfaces.IContainer)

    def __init__(self, context, xml):
        self.xml = xml
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    def __getitem__(self, key):
        # XXX this is not very efficient
        for node in self.xml.iterchildren():
            if node.get('{http://namespaces.zeit.de/CMS/cp}__name__') != key:
                continue
            element_type = node.get('{http://namespaces.zeit.de/CMS/cp}type')
            element = zope.component.getMultiAdapter(
                (self, node),
                zeit.content.cp.interfaces.IElement,
                name=element_type)
            return zope.container.contained.contained(element, self, key)
        raise KeyError(key)

    def __iter__(self):
        for node in self.xml.iterchildren():
            key = node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            if key is not None:
                yield key

    def keys(self):
        return list(self.__iter__())

    def add(self, item):
        name = self._add(item)
        zope.event.notify(zope.container.contained.ObjectAddedEvent(
            item, self, name))

    def _add(self, item):
        name = item.__name__
        if name:
            if name in self:
                raise zope.container.interfaces.DuplicateIDError(name)
        else:
            name = str(uuid.uuid4())
        item.__name__ = name
        self.xml.append(item.xml)
        return name

    def updateOrder(self, order):
        if not isinstance(order, (tuple, list)):
            raise TypeError('order must be tuple or list, got %s.' %
                            type(order))
        if set(order) != set(self.keys()):
            raise ValueError('order must have the same keys.')
        objs = dict(self.items())
        for key in order:
            self._delete(key)
        for key in order:
            self._add(objs[key])
        zope.event.notify(
            zope.container.contained.ContainerModifiedEvent(self))

    def __delitem__(self, key):
        item = self._delete(key)
        zope.event.notify(
            zope.container.contained.ObjectRemovedEvent(item, self, key))

    def _delete(self, key):
        item = self[key]
        item.xml.getparent().remove(item.xml)
        return item

    def __repr__(self):
        return object.__repr__(self)


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()])


class Region(Container):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)


class Lead(Region):

    zope.interface.implements(zeit.content.cp.interfaces.ILead,
                              zeit.content.cp.interfaces.IArea)

    __name__ = 'lead'


class Informatives(Region):

    zope.interface.implements(zeit.content.cp.interfaces.IInformatives,
                              zeit.content.cp.interfaces.IArea)

    __name__ = 'informatives'


class Mosaic(Container):

    zope.interface.implements(zeit.content.cp.interfaces.IMosaic,
                              zeit.content.cp.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    __name__ = 'teaser-mosaic'


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.content.cp.interfaces.IContainer)
def container_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)
