# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces

import zeit.cms.browser.listing
import zeit.content.link.interfaces


class LinkListRepresentation(
    zeit.cms.browser.listing.CommonListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.content.link.interfaces.ILink,
                          zope.publisher.interfaces.IPublicationRequest)
    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        return (super(LinkListRepresentation, self).searchableText
                + self.context.url)
