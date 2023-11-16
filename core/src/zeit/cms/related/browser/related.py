import zope.component
import zope.interface

import zeit.cms.content.interfaces
import zeit.cms.related.related


@zope.component.adapter(
    zeit.cms.related.related.RelatedContent, zeit.cms.content.interfaces.ICMSContentSource
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def related_content_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
    )
