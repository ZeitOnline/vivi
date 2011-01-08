# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import lxml.objectify
import sys
import xml.sax.saxutils
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.related.related
import zope.app.keyreference.interfaces
import zope.component
import zope.schema.interfaces


class ObjectPathProperty(object):
    """Property which is stored in an XML tree."""

    def __init__(self, path, field=None):
        if path is None:
            # This is the root itself.
            self.path = None
        else:
            self.path = lxml.objectify.ObjectPath(path)
        self.field = field

    def __get__(self, instance, class_):
        node = self.getNode(instance)
        if node is None:
            return None
        if zope.schema.interfaces.IFromUnicode.providedBy(self.field):
            try:
                return self.field.fromUnicode(unicode(node))
            except zope.schema.interfaces.ValidationError:
                # Fall back to not using the field when the validaion fails.
                pass
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
        if isinstance(node, lxml.objectify.NoneElement):
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
            value = unicode(value)
            try:
                value = self.field.bind(instance).fromUnicode(value)
            except ValueError:
                value = self.field.missing_value
        elif isinstance(value, str):
            value = unicode(value)
        return value

    def __set__(self, instance, value):
        if self.field is not None:
            self.field.bind(instance).validate(value)
        if value is None:
            self.getNode(instance).attrib.pop(self.attribute_name, None)
        else:
            if not isinstance(value, basestring):
                value = unicode(value)
            self.getNode(instance).set(self.attribute_name, value)


class MultiPropertyBase(object):

    def __init__(self, path, result_type=tuple, sorted=lambda x: x):
        self.path = lxml.objectify.ObjectPath(path)
        self.result_type = result_type
        self.sorted = sorted

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
        return self.result_type(elem for elem in result if elem is not None)

    def __set__(self, instance, value):
        # Remove nodes.
        tree = instance.xml
        for entry in self.path.find(tree, []):
            entry.getparent().remove(entry)
        # Add new nodes:
        value = self.sorted(value)
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
        return zeit.cms.interfaces.ICMSContent(unique_id, None)

    def __set__(self, instance, value):
        if value is None:
            node = None
        else:
            if self.xml_reference_name:
                node = zope.component.getAdapter(
                    value,
                    zeit.cms.content.interfaces.IXMLReference,
                    name=self.xml_reference_name)
            else:
                node = value.uniqueId
        super(SingleResource, self).__set__(instance, node)

    def __delete__(self, instance):
        self.__set__(instance, None)


class MultiResource(object):

    def __init__(self, path, xml_reference_name=None):
        self.path = path
        self.xml_reference_name = xml_reference_name

    def related(self, instance):
        # XXX: refactor this to be other way around, so that Related is
        # implemented by using MultiResource (#7434)
        result = zeit.cms.related.related.RelatedBase(instance)
        result.path = lxml.objectify.ObjectPath(self.path)
        result.xml_reference_name = self.xml_reference_name
        return result

    def __get__(self, instance, class_):
        return self.related(instance)._get_related()

    def __set__(self, instance, value):
        return self.related(instance)._set_related(value)


def mapAttributes(*names):
    vars = sys._getframe(1).f_locals

    def get_mapper(name):
        def mapper(self):
            return getattr(self.context, name)
        return property(mapper)

    for name in names:
        vars[name] = get_mapper(name)


class DAVConverterWrapper(object):
    """Wraps a property and converts data using dav convert."""

    def __init__(self, wrapped_property, field):
        self.wrapped_property = wrapped_property
        self.field = field

    def __get__(self, instance, class_):
        value = self.wrapped_property.__get__(instance, class_)
        return self.get_converter(instance).fromProperty(value)

    def __set__(self, instance, value):
        value = self.get_converter(instance).toProperty(value)
        self.wrapped_property.__set__(instance, value)

    def get_converter(self, instance):
        field = self.field.bind(instance)
        return zeit.cms.content.interfaces.IDAVPropertyConverter(field)
