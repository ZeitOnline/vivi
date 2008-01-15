# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.content.interfaces
import zeit.cms.content.related


@zope.component.adapter(
    zeit.cms.content.related.RelatedContent,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def related_content_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.context, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
