# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface

import zeit.cms.syndication.interfaces

import zeit.xmleditor.interfaces


REFERENCE_TEMPLATE = u'''\
<xi:include xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:fallback>Der Feed ist im Moment leider nicht erreichbar.</xi:fallback>
</xi:include>'''


@zope.component.adapter(zeit.cms.syndication.interfaces.IFeed)
@zope.interface.implementer(zeit.xmleditor.interfaces.IXMLReference)
def FeedXMLReference(context):
    xml = lxml.objectify.fromstring(REFERENCE_TEMPLATE)
    xml.set('href', context.uniqueId)
    return xml
