# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import uuid
import zeit.edit.block
import zeit.edit.interfaces
import zope.container.contained
import zope.interface


class Base(UserDict.DictMixin,
           zeit.edit.block.Element,
           zope.container.contained.Contained):

    zope.interface.implements(zeit.edit.interfaces.IContainer)

    def __init__(self, context, xml):
        self.xml = xml
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    # Implemented in subclasses

    def _find_item(self, xml_node, name):
        raise NotImplementedError

    def _get_keys(self, xml_node):
        raise NotImplementedError

    def _get_element_type(self, xml_node):
        raise NotImplementedError

    # Default implementation

    def __getitem__(self, key):
        node = self._find_item(self.xml, name=key)
        if node:
            node = node[0]
            element_type = self._get_element_type(node)
            element = zope.component.queryMultiAdapter(
                (self, node),
                zeit.edit.interfaces.IElement,
                name=element_type)
            if element is None:
               return None
            return zope.container.contained.contained(element, self, key)
        raise KeyError(key)

    def __iter__(self):
        return (unicode(k) for k in self._get_keys(self.xml))

    def keys(self):
        return list(iter(self))

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
        __traceback_info__ = (order,)
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
        __traceback_info__ = (key,)
        item = self[key]
        item.xml.getparent().remove(item.xml)
        return item

    def __repr__(self):
        return object.__repr__(self)
