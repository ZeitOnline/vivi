# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Aggregated comments."""

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.article.interfaces
import zope.component
import zope.interface


class AggregatedComments(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.content.article.interfaces.IAggregatedComments)

    comment_id = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IAggregatedComments['comment_id'],
        'http://namespaces.zeit.de/CMS/document', 'comment-id')

    def __init__(self, context):
        self.context = self.__parent__ = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(AggregatedComments)
def webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
