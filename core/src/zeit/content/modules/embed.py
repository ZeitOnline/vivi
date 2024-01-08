from urllib.parse import urlparse

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


@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(grok.Adapter):
    grok.context(zeit.content.modules.interfaces.IEmbed)

    has_thirdparty = True

    @cachedproperty
    def thirdparty_vendors(self):
        return (self.context.domain.split('.')[0],)
