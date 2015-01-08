import logging
import lxml.etree
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zope.annotation
import zope.app.container.interfaces
import zope.component
import zope.interface
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
        return
    return zeit.cms.interfaces.ICMSContent(context.__parent__, None)


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLSource)
@zope.component.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
def xml_source(context):
    """Serialize an xml tree."""
    # Remove proxy so lxml can serialize
    xml = zope.security.proxy.removeSecurityProxy(context.xml)
    return lxml.etree.tostring(
        xml.getroottree(), encoding='UTF-8', xml_declaration=True,
        pretty_print=True)


@zope.interface.implementer(zeit.cms.content.interfaces.IContentSortKey)
@zope.component.adapter(zope.app.container.interfaces.IContained)
def content_sort_key(context):
    weight = 0
    key = context.__name__.lower()
    return (weight, key)
