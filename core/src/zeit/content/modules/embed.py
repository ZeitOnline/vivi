from urllib.parse import urlparse, urlunparse

from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zope.interface

import zeit.cmp.interfaces
import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block


@zope.interface.implementer(zeit.content.modules.interfaces.IEmbed)
class Embed(zeit.edit.block.Element):
    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url', zeit.content.modules.interfaces.IEmbed['url']
    )

    @cachedproperty
    def domain(self):
        return self.extract_domain(self.url)

    @staticmethod
    def extract_domain(url):
        if not url:
            return None
        return '.'.join(urlparse(url).netloc.split('.')[-2:])

    @property
    def preview_url(self):
        if not self.url:
            return None
        parts = urlparse(self.url)
        if not parts.netloc.endswith('dwcdn.net'):  # Could use adapter here
            return None
        path = parts.path.rstrip('/').split('/')
        if len(path) != 3:
            return None
        path = '/'.join(path[:-1]) + '/full.png'
        parts = parts._replace(path=path)
        return urlunparse(parts)


@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(grok.Adapter):
    grok.context(zeit.content.modules.interfaces.IEmbed)

    has_thirdparty = True

    @cachedproperty
    def thirdparty_vendors(self):
        return (self.context.domain.split('.')[0],)
