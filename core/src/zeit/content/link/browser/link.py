import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces

import zeit.cms.browser.listing
import zeit.content.link.interfaces


@zope.component.adapter(
    zeit.content.link.interfaces.ILink, zope.publisher.interfaces.IPublicationRequest
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class LinkListRepresentation(zeit.cms.browser.listing.CommonListRepresentation):
    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        result = [super().searchableText, self.context.url]
        return ' '.join(str(s) for s in result if s)
