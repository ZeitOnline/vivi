import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zope.interface


@zope.interface.implementer(
    zeit.cms.content.interfaces.ICachingTime)
class CachingTime(zeit.cms.content.dav.DAVPropertiesAdapter):

    browser = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICachingTime['browser'],
        zeit.cms.interfaces.IR_NAMESPACE,
        'caching_time')
    server = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICachingTime['server'],
        zeit.cms.interfaces.IR_NAMESPACE,
        'caching_time')
