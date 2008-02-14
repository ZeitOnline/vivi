# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.etree
import gocept.lxml.objectify

import persistent

import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.interfaces
import zeit.content.centerpage.interfaces


CP_TEMPLATE = """\
<centerpage xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
</centerpage>"""


class CenterPage(zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(
        zeit.content.centerpage.interfaces.ICenterPage,
        zeit.cms.content.interfaces.IDAVPropertiesInXML)

    default_template = CP_TEMPLATE


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def centerpageFactory(context):
    cp = CenterPage(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVProperties(cp).update(context.properties)
    return cp


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'centerpage')
resourceFactory = zope.component.adapter(
    zeit.content.centerpage.interfaces.ICenterPage)(resourceFactory)


@zope.interface.implementer(zeit.content.centerpage.interfaces.ICenterPage)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def centerpageFromTemplate(context):
    source = StringIO.StringIO(
        zeit.cms.content.interfaces.IXMLSource(context))
    cp = CenterPage(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(cp).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context))
    return cp
