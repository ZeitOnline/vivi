# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import logging
import lxml.etree
import uuid
import zeit.edit.block
import zeit.edit.interfaces
import zope.container.contained
import zope.interface
import zope.proxy


log = logging.getLogger(__name__)


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
            element = self._get_element_for_node(node)
            if element is None:
                log.warning(
                    'Could not resolve element for %s (tag=%s)',
                    key, node.tag)
                return None
            return zope.container.contained.contained(element, self, key)
        raise KeyError(key)

    def _get_element_for_node(self, node):
        element_type = self._get_element_type(node)
        return zope.component.queryMultiAdapter(
            (self, node),
            zeit.edit.interfaces.IElement,
            name=element_type)

    def __iter__(self):
        return (unicode(k) for k in self._get_keys(self.xml))

    def keys(self):
        return list(iter(self))

    def add(self, item):
        name = self._add(item)
        self._p_changed = True
        zope.event.notify(zope.container.contained.ObjectAddedEvent(
            item, self, name))

    def _add(self, item):
        name = item.__name__
        if name:
            if name in self:
                raise zope.container.interfaces.DuplicateIDError(name)
        else:
            name = self._generate_block_id()
        item.__name__ = name
        self.xml.append(zope.proxy.removeAllProxies(item.xml))
        return name

    def _generate_block_id(self):
        return str(uuid.uuid4())

    def updateOrder(self, order):
        __traceback_info__ = (order, self.keys())
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
        self._p_changed = True
        zope.event.notify(
            zope.container.contained.ContainerModifiedEvent(self))

    def __delitem__(self, key):
        item = self._delete(key)
        self._p_changed = True
        zope.event.notify(
            zope.container.contained.ObjectRemovedEvent(item, self, key))

    def _delete(self, key):
        __traceback_info__ = (key,)
        item = self[key]
        item.xml.getparent().remove(item.xml)
        return item

    def __repr__(self):
        return object.__repr__(self)


class TypeOnAttributeContainer(Base):

    _find_item = lxml.etree.XPath(
        './*[@cms:__name__ = $name]',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))
    _get_keys = lxml.etree.XPath(
        './*/attribute::cms:__name__',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))

    def _get_element_type(self, xml_node):
        return xml_node.get('{http://namespaces.zeit.de/CMS/cp}type')
