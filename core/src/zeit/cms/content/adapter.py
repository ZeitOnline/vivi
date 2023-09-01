import logging
import lxml.etree
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zope.annotation
import zope.component
import zope.interface
import zope.location.interfaces
import zope.security.proxy


logger = logging.getLogger(__name__)


@zope.annotation.factory
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return zeit.connector.resource.WebDAVProperties()


@zope.component.adapter(zeit.connector.interfaces.IWebDAVProperties)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
def webdavproperties_to_cms_content(context):
    if not zope.location.interfaces.ILocation.providedBy(context):
        return None
    return zeit.cms.interfaces.ICMSContent(context.__parent__, None)


class NullTarget:

    def start(self, tag, attrib):
        pass

    def end(self, tag):
        pass

    def data(self, data):
        pass

    def comment(self, text):
        pass

    def close(self):
        pass


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLSource)
@zope.component.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
def xml_source(context):
    """Serialize an xml tree."""
    # Remove proxy so lxml can serialize
    xml = zope.security.proxy.removeSecurityProxy(context.xml)
    serialized = lxml.etree.tostring(
        xml.getroottree(), encoding='UTF-8', xml_declaration=True,
        pretty_print=True)
    # XXX We're seeing memory corruption errors from lxml (BUG-194). This is a
    # safetybelt, so we at least don't put non-wellformed XML into DAV.
    null_parser = lxml.etree.XMLParser(target=NullTarget())
    try:
        lxml.etree.fromstring(serialized, parser=null_parser)
    except Exception:
        logger.error('Serializing %s yielded invalid XML:\n%s',
                     context.uniqueId, serialized)
        raise
    return serialized


@zope.interface.implementer(zeit.cms.content.interfaces.IContentSortKey)
@zope.component.adapter(zope.location.interfaces.IContained)
def content_sort_key(context):
    weight = 0
    key = context.__name__.lower()
    return (weight, key)
