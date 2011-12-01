# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Comment browser integration."""

import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.content.article.comment
import zope.component


@zope.component.adapter(
    zeit.content.article.comment.AggregatedComments,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def comment_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
