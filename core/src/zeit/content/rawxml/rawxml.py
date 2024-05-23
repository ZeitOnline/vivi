import zope.interface
import zope.proxy

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.rawxml.interfaces


@zope.interface.implementer(zeit.content.rawxml.interfaces.IRawXML)
class RawXML(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<your-xml-here/>'
    zeit.cms.content.dav.mapProperties(
        zeit.content.rawxml.interfaces.IRawXML, zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, ('title',)
    )


class RawXMLType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = RawXML
    interface = zeit.content.rawxml.interfaces.IRawXML
    title = _('Raw XML')
    type = 'rawxml'
    addform = zeit.cms.type.SKIP_ADD
