from zeit.cms.i18n import MessageFactory as _
import copy
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.rawxml.interfaces
import zope.interface
import zope.proxy


@zope.interface.implementer(zeit.content.rawxml.interfaces.IRawXML)
class RawXML(zeit.cms.content.xmlsupport.XMLContentBase):

    default_template = '<your-xml-here/>'
    zeit.cms.content.dav.mapProperties(
        zeit.content.rawxml.interfaces.IRawXML,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('title',))


class RawXMLType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = RawXML
    interface = zeit.content.rawxml.interfaces.IRawXML
    title = _('Raw XML')
    type = 'rawxml'
    addform = zeit.cms.type.SKIP_ADD


@zope.component.adapter(zeit.content.rawxml.interfaces.IRawXML)
class RawXMLMetadataUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add content of xmlreference to xml reference."""

    def update(self, xml_node, suppress_errors=False):
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
