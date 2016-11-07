import zope.component
import zope.publisher.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.interfaces


class CMSContentListRepresentation(
        zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing unknown content resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.__name__

    @property
    def searchableText(self):
        return self.title

    page = volume = year = ressort = workflowState = modifiedBy = author = None
