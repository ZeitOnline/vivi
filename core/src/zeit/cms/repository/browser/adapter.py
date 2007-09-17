# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.publisher.interfaces
import zope.traversing.browser
import zope.cachedescriptors.property

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.interfaces
import zeit.cms.repository.interfaces


class UnknownResourceListing(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing unknown content resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.repository.interfaces.IUnknownResource,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.__name__

    @property
    def searchableText(self):
        return self.title

    @property
    def metadata(self):
        url = zope.traversing.browser.absoluteURL(self, self.request)
        id = self.context.__name__
        return ('<span class="Metadata">%s</span><span'
                ' class="DeleteId">%s</span>' %(url, id))

    page = volume = year = ressort = workflowState = modifiedBy = author = None


class CollectionListRepresentation(
    zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.repository.interfaces.ICollection,
                          zope.publisher.interfaces.IPublicationRequest)

    author = subtitle = byline = ressort = volume = page = year = None

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return self.context.__name__

    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        return self.title
