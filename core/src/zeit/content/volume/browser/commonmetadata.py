import zeit.cms.browser.listing
import zope.interface
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.content.volume.browser.interfaces


class CommonMetadataContentListRepresentation(
        zeit.cms.content.browser.commonmetadata.CommonMetadataListRepresentation,
        zeit.content.volume.browser.content.ContentListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.content.interfaces.ICommonMetadata,
                          zeit.content.volume.browser.interfaces.ITocLayer)
