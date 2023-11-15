import zope.component
import zope.publisher.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.interfaces


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent, zope.publisher.interfaces.IPublicationRequest
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class CMSContentListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing unknown content resources"""

    @property
    def title(self):
        return self.__name__

    @property
    def searchableText(self):
        return self.title

    page = volume = year = ressort = workflowState = modifiedBy = author = None
