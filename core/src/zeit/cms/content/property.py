# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import sys

import lxml.objectify

import transaction

import zope.component

import zope.app.keyreference.interfaces

import zeit.cms.repository.interfaces


class ObjectPathProperty(object):
    """Property which is stored in an XML tree."""

    def __init__(self, path):
        if path is None:
            # This is the root itself.
            self.path = None
        else:
            self.path = lxml.objectify.ObjectPath(path)

    def __get__(self, instance, class_):
        node = self.getNode(instance)
        if node is not None:
            try:
                value = node.pyval
            except AttributeError:
                return None
            if isinstance(value, str):
                # This is save because lxml only uses str for optimisation
                # reasons and unicode when non us-ascii chars are in the str:
                value = unicode(value)
            return value


    def __set__(self, instance, value):
        if self.path is None:
            # We cannot just set the new value because setting detaches the
            # instance.xml from the original tree leaving instance independet
            # of the xml-tree. 
            node = instance.xml
            parent = node.getparent()
            new_node = lxml.objectify.E.root(
                getattr(lxml.objectify.E, node.tag)(value))[node.tag]
            parent.replace(node, new_node)
            instance.xml = new_node
        else:
            self.path.setattr(instance.xml, value)

    def getNode(self, instance):
        if self.path is None:
            return instance.xml
        try:
            node = self.path.find(instance.xml)
        except AttributeError:
            return None
        return node


class ObjectPathAttributeProperty(ObjectPathProperty):
    """Property which is stored in an XML tree."""

    def __init__(self, path, attribute_name, field=None):
        super(ObjectPathAttributeProperty, self).__init__(path)
        self.attribute_name = attribute_name
        self.field = field

    def __get__(self, instance, class_):
        value = self.getNode(instance).get(self.attribute_name)
        if self.field is not None and isinstance(value, basestring):
            # If we've got a field assigned, let the field convert the value.
            # But only if it is a string. This is mostly the case, but if the
            # attribute is missing `value` is none.
            value = self.field.fromUnicode(value)
        elif isinstance(value, str):
            value = unicode(value)
        return value

    def __set__(self, instance, value):
        if self.field is not None:
            self.field.validate(value)
        if not isinstance(value, basestring):
            value = unicode(value)
        self.getNode(instance).set(self.attribute_name, value)


class AttributeProperty(object):
    """Attribute nodes reside in the head."""

    def __init__(self, namespace, name):
        self.xpath = '//head/attribute[@ns="%s" and @name="%s"]' % (
                namespace, name)
        self.path = lxml.objectify.ObjectPath('.head.attribute')
        self.namespace = namespace
        self.name = name

    def __get__(self, instance, class_):
        node = instance.xml.find(self.xpath)
        if node is not None:
            value = node.pyval
            if isinstance(value, str):
                value = unicode(value)
            return value

    def __set__(self, instance, value):
        __traceback_info__ = (instance, self.xpath, value)
        self.delAttribute(instance)
        self.addAttribute(instance, value)

    def __delete__(self, instance):
        self.delAttribute(instance)

    def addAttribute(self, instance, value):
        root = instance.xml
        self.path.addattr(root, value)
        node = self.path.find(root)[-1]
        node.set('ns', self.namespace)
        node.set('name', self.name)

    def delAttribute(self, instance):
        root = instance.xml
        for node in root.findall(self.xpath):
            parent = node.getparent()
            parent.remove(node)


class MultipleAttributeProperty(AttributeProperty):
    """A property with multiple values."""

    def __get__(self, instance, class_):
        nodes = instance.xml.findall(self.xpath)
        result = []
        for node in nodes:
            value = node.pyval
            if isinstance(value, str):
                value = unicode(value)
            result.append(value)
        return frozenset(result)

    def __set__(self, instance, values):
        self.delAttribute(instance)
        for value in values:
            self.addAttribute(instance, value)


class MultiPropertyBase(object):

    def __init__(self, path):
        self.path = lxml.objectify.ObjectPath(path)

    def __get__(self, instance, class_):
        tree = instance.xml
        result = []
        try:
            element_set = self.path.find(tree)
        except AttributeError:
            # no keywords
            element_set = []
        for node in element_set:
            result.append(self._element_factory(node, tree))
        return tuple(result)

    def __set__(self, instance, value):
        # Remove nodes.
        tree = instance.xml
        for entry in self.path.find(tree, []):
            entry.getparent().remove(entry)
        # Add new nodes:
        self.path.setattr(tree, [self._node_factory(entry, tree)
                                 for entry in value])

    def _element_factory(self, node, tree):
        raise NotImplementedError("Implemented in sub classes.")

    def _node_factory(self, entry, tree):
        raise NotImplementedError("Implemented in sub classes.")


class SimpleMultiProperty(MultiPropertyBase):

    def _element_factory(self, node, tree):
        return unicode(node)

    def _node_factory(self, entry, tree):
        return entry


class ResourceSet(MultipleAttributeProperty):

    def __get__(self, instance, class_):
        ids = super(ResourceSet, self).__get__(instance, class_)
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        objects = []
        for id in ids:
            try:
                obj = repository.getContent(id)
            except KeyError:
                continue
            objects.append(obj)
        return frozenset(objects)

    def __set__(self, instance, values):
        values = sorted([ob.uniqueId for ob in values])
        super(ResourceSet, self).__set__(instance, values)


class SingleResource(ObjectPathProperty):

    def __get__(self, instance, class_):
        unique_id = super(SingleResource, self).__get__(instance, class_)
        if not unique_id:
            return None
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        try:
            return repository.getContent(unique_id)
        except KeyError:
            return None

    def __set__(self, instance, value):
        super(SingleResource, self).__set__(instance, value.uniqueId)


class KeyReferenceTuple(object):

    def __init__(self, attribute):
        self.attribute = attribute

    def __get__(self, instance, class_):
        if instance is None:
            return self
        result = []
        for key_ref in getattr(instance, self.attribute):
            try:
                obj = key_ref()
            except KeyError:
                continue
            result.append(obj)

        return tuple(result)

    def __set__(self, instance, values):
        new_value = tuple(zope.app.keyreference.interfaces.IKeyReference(obj)
                          for obj in values)
        setattr(instance, self.attribute, new_value)


def mapAttributes(*names):
    vars = sys._getframe(1).f_locals

    def get_mapper(name):
        def mapper(self):
            return getattr(self.context, name)
        return property(mapper)

    for name in names:
        vars[name] = get_mapper(name)
