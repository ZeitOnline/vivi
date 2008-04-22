# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.connector.interfaces

import zeit.cms.content.adapter
import zeit.cms.syndication.feed


class BodyContainer(zeit.cms.syndication.feed.Feed):
    """A body/container style channel."""

    @property
    def entries(self):
        return self.xml.body.container


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def bodyContainerFactory(context):
    feed = BodyContainer(context.data)
    zeit.connector.interfaces.IWebDAVWriteProperties(feed).update(
        context.properties)
    return feed


bodyContainerResourceFactory = (
    zeit.cms.content.adapter.xmlContentToResourceAdapterFactory('channel_cp'))
bodyContainerResourceFactory = zope.component.adapter(
    BodyContainer)(bodyContainerResourceFactory)
