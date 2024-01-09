import zope.component
import zope.interface

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.content.rawxml.interfaces


@zope.component.adapter(
    zeit.content.rawxml.interfaces.IRawXML, zeit.cms.browser.interfaces.ICMSLayer
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class ListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    author = ressort = page = volume = year = None
    type = 'rawxml'

    @property
    def title(self):
        return self.context.title

    searchableText = title
