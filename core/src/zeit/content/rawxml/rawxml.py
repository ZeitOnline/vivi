# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import copy

import zope.interface
import zope.proxy

import zeit.cms.content.xmlsupport
import zeit.cms.content.dav
import zeit.cms.interfaces

import zeit.content.rawxml.interfaces


class RawXML(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implementsOnly(
        zeit.content.rawxml.interfaces.IRawXML)

    default_template = u'<your-xml-here/>'
    zeit.cms.content.dav.mapProperties(
        zeit.content.rawxml.interfaces.IRawXML,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('title',))


resourceFactory = zeit.cms.content.adapter.xmlContentToResourceAdapterFactory(
    'rawxml')
resourceFactory = zope.component.adapter(
        zeit.content.rawxml.interfaces.IRawXML)(resourceFactory)


contentFactory = zeit.cms.content.adapter.xmlContentFactory(RawXML)


class RawXMLMetadataUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add content of xmlreference to xml reference."""

    zope.component.adapts(zeit.content.rawxml.interfaces.IRawXML)

    def update(self, xml_node):
        # Since we're adding arbitrary xml, we need to mark nodes we've
        # inserted to be able to remove them later. The following attribute is
        # "ours":
        attribute_name = ('{http://namespaces.zeit.de/CMS/RawXML}'
                          'isSyndicatedRawXML')

        # Remove nodes we've added
        remove_nodes = []
        for node in xml_node.iterchildren():
            if node.get(attribute_name):
                remove_nodes.append(node)
        for node in remove_nodes:
            node.getparent().remove(node)

        # Append new nodes
        node = copy.deepcopy(
            zope.proxy.removeAllProxies(self.context.xml))
        node.set(attribute_name, 'true')
        xml_node.append(node)
