import collections.abc
import grokcore.component as grok
import logging
import lxml.etree
import uuid
import zeit.edit.block
import zeit.edit.interfaces
import zope.container.contained
import zope.interface
import zope.location.interfaces
import zope.proxy
import zope.security.proxy


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.edit.interfaces.IContainer)
class Base(
    zeit.edit.block.Element, zope.container.contained.Contained, collections.abc.MutableMapping
):
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
            try:
                return list(self.values())[position]
            except IndexError:
                raise KeyError(key)

        node = self._find_item(self.xml, name=key)
        if node:
            node = node[0]
            element = self._get_element_for_node(node)
            if element is None:
                log.warning('Unknown element tag=%s, id=%s', node.tag, key)
                element = self._get_element_for_node(node, zeit.edit.block.UnknownBlock.type)
            return zope.container.contained.contained(element, self, key)
        raise KeyError(key)

    def _get_element_for_node(self, node, element_type=None):
        if element_type is None:
            element_type = self._get_element_type(node)
        return zope.component.queryMultiAdapter(
            (self, node), zeit.edit.interfaces.IElement, name=element_type
        )

    def __iter__(self):
        return (str(k) for k in self._get_keys(self.xml))

    def __len__(self):
        return len(self.keys())

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def keys(self):
        return list(iter(self))

    def values(self):
        return [self[x] for x in self]

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

    def insert(self, position, item):
        """Insert item at given position into container.

        We cannot use insert to modify the XML, since the XML has heterogeneous
        child types. This means that XML childs and container childs can be
        different! Therefore we have to use append and updateOrder, which only
        sorts the childs of the container. This is the reason why we use add +
        updateOrder instead of inserting directly into the correct position of
        the XML tree.

        Since we used updateOrder we have to send an IOrderUpdatedEvent, but
        after the item was added / moved. Therefore we suppress the event in
        updateOrder and create it explicitely at the end. (It's a subclass of
        IContainerModifiedEvent, thus we can replace the modified event with
        the updated event.)

        """
        is_new = item.__name__ is None

        keys = self.keys()
        self._add(item)
        keys_before_sort = self.keys()

        keys.insert(position, item.__name__)
        self.updateOrder(keys, send_event=False)
        self._p_changed = True

        event = self._contained_event(item, is_new)
        if event is not None:
            zope.event.notify(event)
            zope.event.notify(zeit.edit.interfaces.OrderUpdatedEvent(self, *keys_before_sort))

    def add(self, item):
        is_new = item.__name__ is None
        self._add(item)
        self._p_changed = True

        event = self._contained_event(item, is_new)
        if event is not None:
            zope.event.notify(event)
            zope.container.contained.notifyContainerModified(self)

    def _contained_event(self, item, is_new):
        """Re-implementation of zope.container.contained.containedEvent

        We cannot reuse it, since we already set __name__ and __parent__.
        Therefore containedEvent would assume that nothing changed and returns
        no event.

        """
        event = None
        if item.__parent__ != self:
            oldparent = item.__parent__
            item.__parent__ = self
            event = zope.container.contained.ObjectMovedEvent(
                item, oldparent, item.__name__, self, item.__name__
            )
        elif is_new:
            event = zope.container.contained.ObjectAddedEvent(item, self, item.__name__)

        return event

    def _add(self, item):
        item.__name__ = self._get_unique_name(item)
        self.xml.append(zope.proxy.removeAllProxies(item.xml))

        return item.__name__

    def _get_unique_name(self, item):
        name = item.__name__
        if name:
            if name in self:
                raise zope.container.interfaces.DuplicateIDError(name)
        else:
            name = self._generate_block_id()
        return name

    def create_item(self, type_, position=None):
        return zope.component.getAdapter(self, zeit.edit.interfaces.IElementFactory, name=type_)(
            position
        )

    def _generate_block_id(self):
        return 'id-' + str(uuid.uuid4())

    def updateOrder(self, order, send_event=True):
        old_order = self.keys()
        __traceback_info__ = (order, old_order)
        if not zope.security.proxy.isinstance(order, (tuple, list)):
            raise TypeError('order must be tuple or list, got %s.' % type(order))
        if set(order) != set(old_order):
            raise ValueError('order must have the same keys.')
        objs = dict(self.items())
        for key in order:
            self._delete(key)
        for key in order:
            self._add(objs[key])

        self._p_changed = True
        if send_event:
            zope.event.notify(zeit.edit.interfaces.OrderUpdatedEvent(self, *old_order))

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

    def filter_values(self, *interfaces):
        for child in self.values():
            if any(x.providedBy(child) for x in interfaces):
                yield child

    def find_first(self, interface):
        result = list(self.filter_values(interface))
        return result[0] if result else None

    def __delitem__(self, key):
        item = self._delete(key)
        self._p_changed = True

        # We cannot reuse zope.container.contained.uncontained, since it would
        # set __name__ and __parent__ to None, which cannot be persisted to XML
        zope.event.notify(zope.container.contained.ObjectRemovedEvent(item, self, key))
        zope.container.contained.notifyContainerModified(self)

    def _delete(self, key):
        __traceback_info__ = (key,)
        item = self[key]
        item.xml.getparent().remove(item.xml)
        return item

    def __repr__(self):
        return zeit.edit.block.Element.__repr__(self)


class TypeOnAttributeContainer(Base):
    _find_item = lxml.etree.XPath(
        './*[@cms:__name__ = $name]', namespaces={'cms': 'http://namespaces.zeit.de/CMS/cp'}
    )
    _get_keys = lxml.etree.XPath(
        './*/@cms:__name__', namespaces={'cms': 'http://namespaces.zeit.de/CMS/cp'}
    )

    def _get_element_type(self, xml_node):
        return xml_node.get('{http://namespaces.zeit.de/CMS/cp}type', '__invalid__')


@grok.implementer(zope.location.interfaces.ISublocations)
class Sublocations(grok.Adapter):
    """We don't want to dispatch events that happen to the content object
    (like being added to the Workingcopy) to their IElement children.
    """

    grok.context(zeit.edit.interfaces.IContainer)

    def sublocations(self):
        return []
