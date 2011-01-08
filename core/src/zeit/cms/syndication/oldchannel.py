# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.adapter
import zeit.cms.syndication.feed
import zeit.cms.type
import zeit.connector.interfaces
import zope.component
import zope.interface


class BodyContainer(zeit.cms.syndication.feed.Feed):
    """A body/container style channel."""

    @property
    def entries(self):
        return self.xml.body.container



class BodyContainerType(zeit.cms.type.XMLContentTypeDeclaration):

    type = 'channel_cp'
    factory = BodyContainer
    interface = BodyContainer  # Only register for class
    register_as_type = False
