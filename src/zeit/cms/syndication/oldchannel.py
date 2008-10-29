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


bodyContainerFactory = zeit.cms.content.adapter.xmlContentFactory(
    BodyContainer)


bodyContainerResourceFactory = (
    zeit.cms.content.adapter.xmlContentToResourceAdapterFactory('channel_cp'))
bodyContainerResourceFactory = zope.component.adapter(
    BodyContainer)(bodyContainerResourceFactory)
