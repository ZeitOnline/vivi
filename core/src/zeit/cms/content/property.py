# Copyright (c) 2007 gocept gmbh & co. kg
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
                return node.pyval
            except AttributeError:
                return None

    def __set__(self, instance, value):
        if self.path is None:
            # This is really hairy. We replace the value. This detaches the
            # instance.xml from the original tree leaving instance independet
            # of the xml-tree. This means we need to find the replaced node in 
            # the xml-tree and re-attach. *gaah*
            node = instance.xml
            index = node[:].index(node)
            parent = node.getparent()
            node[index] = value
            instance.xml = parent[node.tag][index]
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
            return node.pyval

    def __set__(self, instance, value):
        __traceback_info__ = (instance, self.xpath, value)
        self.delAttribute(instance)
        self.addAttribute(instance, value)

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
        return frozenset(node.pyval for node in nodes)

    def __set__(self, instance, values):
        self.delAttribute(instance)
        for value in values:
            self.addAttribute(instance, value)


class ResourceProperty(MultipleAttributeProperty):

    def __get__(self, instance, class_):
        ids = super(ResourceProperty, self).__get__(instance, class_)
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        objects = []
        for id in ids:
            objects.append(repository.getContent(id))
        return frozenset(objects)

    def __set__(self, instance, values):
        values = [ob.uniqueId for ob in values]
        super(ResourceProperty, self).__set__(instance, values)


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
