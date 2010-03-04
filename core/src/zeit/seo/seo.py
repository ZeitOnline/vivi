# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Search engine optimisation."""

import zope.component
import zope.interface

import zeit.connector.interfaces
import zeit.cms.interfaces
import zeit.cms.content.dav

import zeit.seo.interfaces


class SEO(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.seo.interfaces.ISEO)

    html_title = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['html_title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'html-meta-title')

    html_description = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['html_description'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'html-meta-description')

    meta_robots = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['meta_robots'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'html-meta-robots')

    def __init__(self, context):
        self.context = context


@zope.component.adapter(SEO)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def seo_dav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)
