import zope.component
import zope.interface

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.content.interfaces


@zope.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.browser.interfaces.ICMSLayer
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class CommonMetadataListRepresentation(zeit.cms.browser.listing.CommonListRepresentation):
    pass
