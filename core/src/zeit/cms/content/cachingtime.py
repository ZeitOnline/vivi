import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zope.interface


@zope.interface.implementer(
    zeit.cms.content.interfaces.ICachingTime)
class CachingTime(zeit.cms.content.dav.DAVPropertiesAdapter):

    browser = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICachingTime['browser'],
        'zeit.web',
        'browser')
    server = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICachingTime['server'],
        'zeit.web',
        'server')
