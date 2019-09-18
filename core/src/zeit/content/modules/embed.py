from urlparse import urlparse
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


class Embed(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IEmbed)

    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url', zeit.content.modules.interfaces.IEmbed['url'])

    @cachedproperty
    def domain(self):
        return self.extract_domain(self.url)

    @staticmethod
    def extract_domain(url):
        if not url:
            return None
        return '.'.join(urlparse(url).netloc.split('.')[-2:])

    @cachedproperty
    def template(self):
        source = zeit.content.modules.interfaces.EMBED_PROVIDER_SOURCE.factory
        return source.find(self.domain)
