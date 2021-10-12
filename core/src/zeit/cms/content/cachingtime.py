import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces


@zope.interface.implementer(
    zeit.cms.content.interfaces.ICachingTime)
class CachingTime(zeit.cms.content.dav.DAVPropertiesAdapter):

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICachingTime,
        zeit.cms.interfaces.ZEITWEB_NAMESPACE,
        ('browser', 'server')
    )
