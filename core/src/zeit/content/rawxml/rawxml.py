# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface

import zeit.cms.content.xmlsupport
import zeit.cms.content.dav
import zeit.cms.interfaces

import zeit.content.rawxml.interfaces


class RawXML(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.content.rawxml.interfaces.IRawXML)

    default_template = u'<your-xml-here/>'
    zeit.cms.content.dav.mapProperties(
        zeit.content.rawxml.interfaces.IRawXML,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('title', ))
