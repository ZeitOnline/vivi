import zeit.cms.browser.listing
import zope.interface
import zope.component
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces


class CommonMetadataListRepresentation(
        zeit.cms.browser.listing.CommonListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.content.interfaces.ICommonMetadata,
                          zeit.cms.browser.interfaces.ICMSLayer)
