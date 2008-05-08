# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import sys
import xml.sax.saxutils

import lxml.etree
import lxml.objectify

import transaction

import zope.component

import zope.app.keyreference.interfaces

import zeit.cms.repository.interfaces
import zeit.cms.content.interfaces


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


class Structure(ObjectPathProperty):
    """Structure identified by object path."""

    remove_namespaces = lxml.etree.XSLT(lxml.etree.XML(
        u"""\
        <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
          <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
            <xsl:template match="*">
              <!-- remove element prefix (if any) -->
              <xsl:element name="{local-name()}">
                <!-- process attributes -->
                <xsl:for-each select="@*">
                  <!-- remove attribute prefix (if any) -->
                  <xsl:attribute name="{local-name()}">
                    <xsl:value-of select="."/>
                  </xsl:attribute>
                </xsl:for-each>
                <xsl:apply-templates/>
              </xsl:element>
          </xsl:template>
        </xsl:stylesheet>
    """))

    def __get__(self, instance, class_):
        node = self.getNode(instance)
        if node is None:
            return
        node = lxml.objectify.fromstring(unicode(self.remove_namespaces(node)))
        result = [xml.sax.saxutils.escape(unicode(node))]
        for child in node.iterchildren():
            lxml.objectify.deannotate(child)
            result.append(lxml.etree.tostring(child, encoding=unicode))
        return u''.join(result)

    def __set__(self, instance, value):
        # Objectify value:
        xml = lxml.objectify.fromstring(u'<xml>%s</xml>' % value)
        self.path.setattr(instance.xml, xml)


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
        return tuple(elem for elem in result if elem is not None)

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


class SingleResource(ObjectPathProperty):

    def __init__(self, path, xml_reference_name=None, attributes=None):
        super(SingleResource, self).__init__(path)
        if (xml_reference_name is None) ^ (attributes is None):
            raise ValueError(
                "Either both `xml_reference_name` and `attributes` or neither"
                " must be given.")
        if attributes is not None and not isinstance(attributes, tuple):
            raise ValueError("`attributes` must be tuple, got %s" %
                             type(attributes))
        self.xml_reference_name = xml_reference_name
        self.attributes = attributes

    def __get__(self, instance, class_):
        node = self.getNode(instance)
        if self.attributes and node is not None:
            for attr in self.attributes:
                unique_id = node.get(attr)
                if unique_id:
                    break
        else:
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
        if self.xml_reference_name:
            node = zope.component.getAdapter(
                value,
                zeit.cms.content.interfaces.IXMLReference,
                name=self.xml_reference_name)
        else:
            node = value.uniqueId
        super(SingleResource, self).__set__(instance, node)


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
