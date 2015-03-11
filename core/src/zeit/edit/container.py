import UserDict
import logging
import lxml.etree
import uuid
import zeit.edit.block
import zeit.edit.interfaces
import zope.container.contained
import zope.interface
import zope.proxy
import zope.security.proxy


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

    def index(self, value):
        # A simple implementation would be self.values().index(value), but that
        # won't work in the general case since the abstract implementation of
        # self.values is "self[x] for x in self.keys()", which defeats the
        # purpose of this method.
        raise NotImplementedError

    def _get_element_type(self, xml_node):
        raise NotImplementedError

    # Default implementation

    def __getitem__(self, key):
        try:
            position = int(key)
        except ValueError:
            pass
        else:
            return self.values()[position]

        node = self._find_item(self.xml, name=key)
        if node:
            node = node[0]
            element = self._get_element_for_node(node)
            if element is None:
                log.warning(
                    'Unknown element tag=%s, id=%s',
                    node.tag, key)
                element = self._get_element_for_node(
                    node, zeit.edit.block.UnknownBlock.type)
            return zope.container.contained.contained(element, self, key)
        raise KeyError(key)

    def _get_element_for_node(self, node, element_type=None):
        if element_type is None:
            element_type = self._get_element_type(node)
        return zope.component.queryMultiAdapter(
            (self, node),
            zeit.edit.interfaces.IElement,
            name=element_type)

    def __iter__(self):
        return (unicode(k) for k in self._get_keys(self.xml))

    def keys(self):
        return list(iter(self))

    def slice(self, start, end):
        result = []
        started = False
        for key in self.keys():
            if key == start:
                started = True
            if started:
                result.append(self[key])
            if key == end:
                break
        return result

    def add(self, item):
        name = self._add(item)
        self._p_changed = True

        # Re-implementation of zope.container.contained.containedEvent
        if item.__parent__ != self:
            oldparent = item.__parent__
            item.__parent__ = self
            event = zope.container.contained.ObjectMovedEvent(
                item, oldparent, name, self, name)
        else:
            event = zope.container.contained.ObjectAddedEvent(
                item, self, name)
        zope.event.notify(event)

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

    def create_item(self, type_):
        return zope.component.getAdapter(
            self, zeit.edit.interfaces.IElementFactory, name=type_)()

    def _generate_block_id(self):
        return 'id-' + str(uuid.uuid4())

    def updateOrder(self, order):
        old_order = self.keys()
        __traceback_info__ = (order, old_order)
        if not zope.security.proxy.isinstance(order, (tuple, list)):
            raise TypeError('order must be tuple or list, got %s.' %
                            type(order))
        if set(order) != set(old_order):
            raise ValueError('order must have the same keys.')
        objs = dict(self.items())
        for key in order:
            self._delete(key)
        for key in order:
            self._add(objs[key])
        self._p_changed = True
        zope.event.notify(
            zeit.edit.interfaces.OrderUpdatedEvent(self, *old_order))

    def get_recursive(self, key, default=None):
        item = self.get(key, default)
        if item is not default:
            return item
        for child in self.values():
            if zeit.edit.interfaces.IContainer.providedBy(child):
                item = child.get_recursive(key, default)
                if item is not default:
                    return item
        return default

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
        './*/@cms:__name__',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))

    def _get_element_type(self, xml_node):
        return xml_node.get('{http://namespaces.zeit.de/CMS/cp}type')
