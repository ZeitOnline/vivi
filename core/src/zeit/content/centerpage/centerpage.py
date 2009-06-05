# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import StringIO
import gocept.lxml.objectify
import lxml.etree
import persistent
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.centerpage.interfaces
import zope.app.container.contained
import zope.component
import zope.interface


CP_TEMPLATE = """\
<centerpage xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
</centerpage>"""


class CenterPage(zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(
        zeit.content.centerpage.interfaces.ICenterPage,
        zeit.cms.content.interfaces.IDAVPropertiesInXML,
        zeit.cms.interfaces.IEditorialContent)

    default_template = CP_TEMPLATE


class CenterPageType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = CenterPage
    interface = zeit.content.centerpage.interfaces.ICenterPage
    title = _('Centerpage')
    type = 'centerpage'


@zope.interface.implementer(zeit.content.centerpage.interfaces.ICenterPage)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def centerpageFromTemplate(context):
    source = StringIO.StringIO(
        zeit.cms.content.interfaces.IXMLSource(context))
    cp = CenterPage(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(cp).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context))
    return cp
