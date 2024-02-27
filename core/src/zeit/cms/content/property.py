import sys
import xml.sax.saxutils

import lxml.etree
import lxml.objectify
import zope.component
import zope.schema.interfaces

from zeit.cms.content.util import create_parent_nodes
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.resource


class ObjectPathProperty:
    """Property which is stored in an XML node."""

    def __init__(self, path, field=None, use_default=False):
        if path is None:
            # This is the root itself.
            self.path = None
        else:
            self.path = lxml.objectify.ObjectPath(path)
        self.field = field
        self.use_default = use_default

    def __get__(self, instance, class_):
        if instance is None:
            return self
        node = self.getNode(instance)
        if node is None:
            if self.field:
                if self.use_default:
                    return self.field.default
                else:
                    return self.field.missing_value
            else:
                return None
        if zope.schema.interfaces.IFromUnicode.providedBy(self.field):
            try:
                if node.text is not None:
                    return self.field.bind(instance).fromUnicode(str(node.text))
            except zope.schema.interfaces.ValidationError:
                # Fall back to not using the field when the validation fails.
                pass
        return node.text or ''

    def __set__(self, instance, value):
        if self.path is None:
            # We cannot just set the new value because setting detaches the
            # instance.xml from the original tree leaving instance independent
            # of the xml-tree.
            root = instance.xml
            parent = root.getparent()
            node = lxml.etree.Element(root.tag)
            node.text = value
            parent.replace(root, node)
            instance.xml = node
        else:
            if value is not None:
                parent, name = create_parent_nodes(self.path, instance.xml)
                node = parent.find(name)
                if node is None:
                    node = lxml.etree.Element(name)
                    parent.append(node)
                # XXX Previously this used self.path.setattr, relying on
                # lxml.objectify type conversion (int and bool mostly).
                # We probably should use self.field instead?
                if isinstance(value, bool):
                    value = str(value).lower()
                node.text = str(value)
            else:
                node = self.getNode(instance)
                if node is not None:
                    node.getparent().remove(node)

    def getNode(self, instance):
        if self.path is None:
            return instance.xml
        return self.path.find(instance.xml, None)


class Structure(ObjectPathProperty):
    """Structure identified by object path."""

    remove_namespaces = lxml.etree.XSLT(
        lxml.etree.XML(
            """\
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
    """
        )
    )

    def __get__(self, instance, class_):
        node = self.getNode(instance)
        if node is None:
            return self.field.missing_value if self.field else None
        node = lxml.etree.fromstring(str(self.remove_namespaces(node)))
        result = [xml.sax.saxutils.escape(node.text or '')]
        for child in node.iterchildren():
            result.append(lxml.etree.tostring(child, encoding=str))
        return ''.join(result)

    def __set__(self, instance, value):
        if self.field and value is self.field.missing_value:
            value = None
        else:
            value = lxml.etree.fromstring('<xml>%s</xml>' % value)
        self.path.setattr(instance.xml, value)


class ObjectPathAttributeProperty(ObjectPathProperty):
    """Property which is stored in an XML attribute."""

    def __init__(self, path, attribute_name, field=None, use_default=False):
        super().__init__(path, field, use_default)
        self.attribute_name = attribute_name

    def __get__(self, instance, class_):
        if instance is None:
            return self
        try:
            value = self.getNode(instance).get(self.attribute_name)
        except AttributeError:
            return None
        if value is None:
            if self.field:
                if self.use_default:
                    return self.field.default
                else:
                    return self.field.missing_value
            else:
                return None
        value = str(value)
        if zope.schema.interfaces.IFromUnicode.providedBy(self.field):
            try:
                return self.field.bind(instance).fromUnicode(value)
            except zope.schema.interfaces.ValidationError:
                pass
        return value

    def __set__(self, instance, value):
        if value is None:
            self.getNode(instance).attrib.pop(self.attribute_name, None)
        else:
            if not isinstance(value, str):
                value = str(value)
            node = self.getNode(instance)
            if node is None:
                super().__set__(instance, '')
                node = self.getNode(instance)
            node.set(self.attribute_name, value)


class MultiPropertyBase:
    def __init__(self, path, result_type=tuple, sorted=lambda x: x):
        self.path = lxml.objectify.ObjectPath(path)
        self.result_type = result_type
        self.sorted = sorted

    def __get__(self, instance, class_):
        if instance is None:
            return self
        tree = instance.xml
        result = []
        anchor = self.path.find(tree, None)
        if anchor is not None:
            for node in anchor.getparent().iterchildren(anchor.tag):
                result.append(self._element_factory(node))
        return self.result_type(elem for elem in result if elem is not None)

    def __set__(self, instance, value):
        # Remove nodes.
        tree = instance.xml
        node = self.path.find(tree, None)
        if node is not None:
            for entry in node.getparent().iterchildren(node.tag):
                entry.getparent().remove(entry)
        # Add new nodes:
        value = self.sorted(value)
        self.path.setattr(tree, [self._node_factory(entry) for entry in value])

    def _element_factory(self, node):
        raise NotImplementedError('Implemented in sub classes.')

    def _node_factory(self, entry):
        raise NotImplementedError('Implemented in sub classes.')


class SimpleMultiProperty(MultiPropertyBase):
    def _element_factory(self, node):
        return node.text

    def _node_factory(self, entry):
        name = str(self.path).split('.')[-1]
        return getattr(lxml.builder.E, name)(entry)


class SingleResource(ObjectPathProperty):
    def __init__(self, path, xml_reference_name=None, attributes=None):
        super().__init__(path)
        if (xml_reference_name is None) ^ (attributes is None):
            raise ValueError(
                'Either both `xml_reference_name` and `attributes` or neither' ' must be given.'
            )
        if attributes is not None and not isinstance(attributes, tuple):
            raise ValueError('`attributes` must be tuple, got %s' % type(attributes))
        self.xml_reference_name = xml_reference_name
        self.attributes = attributes

    def __get__(self, instance, class_):
        if instance is None:
            return self
        node = self.getNode(instance)
        if self.attributes and node is not None:
            for attr in self.attributes:
                unique_id = node.get(attr)
                if unique_id:
                    break
        else:
            unique_id = super().__get__(instance, class_)
        if not unique_id:
            return None
        return zeit.cms.interfaces.ICMSContent(unique_id, None)

    def __set__(self, instance, value):
        if value is None:
            node = None
        else:
            if self.xml_reference_name:
                node = zope.component.getAdapter(
                    value, zeit.cms.content.interfaces.IXMLReference, name=self.xml_reference_name
                )
            else:
                node = value.uniqueId
        super().__set__(instance, node)

    def __delete__(self, instance):
        self.__set__(instance, None)


def mapAttributes(*names):
    vars = sys._getframe(1).f_locals

    def get_mapper(name):
        def mapper(self):
            return getattr(self.context, name)

        return property(mapper)

    for name in names:
        vars[name] = get_mapper(name)


class DAVConverterWrapper:
    """Wraps a property and converts data using dav convert."""

    DUMMY_PROPERTIES = zeit.connector.resource.WebDAVProperties()

    def __init__(self, wrapped_property, field):
        self.wrapped_property = wrapped_property
        self.field = field

    def __get__(self, instance, class_):
        if instance is None:
            return self
        value = self.wrapped_property.__get__(instance, class_)
        if value == self.field.missing_value:
            return value
        return self.get_converter(instance).fromProperty(value)

    def __set__(self, instance, value):
        value = self.get_converter(instance).toProperty(value)
        self.wrapped_property.__set__(instance, value)

    def get_converter(self, instance):
        field = self.field.bind(instance)
        return zope.component.getMultiAdapter(
            (field, self.DUMMY_PROPERTIES), zeit.cms.content.interfaces.IDAVPropertyConverter
        )
