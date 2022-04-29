
import zope.publisher.interfaces.browser

import zeit.cms.browser.listing
import zeit.cms.browser.interfaces

import zeit.content.infobox.interfaces
import zeit.content.infobox.reference


@zope.component.adapter(
    zeit.content.infobox.interfaces.IInfobox,
    zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class ListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    author = ressort = page = volume = year = ''

    @property
    def title(self):
        return self.context.supertitle

    searchableText = title


@zope.component.adapter(
    zeit.content.infobox.reference.InfoboxReference,
    zeit.content.infobox.interfaces.InfoboxSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def infoboxreference_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
