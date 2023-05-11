from urllib.parse import urlparse
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zeit.cmp.interfaces
import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


@zope.interface.implementer(zeit.content.modules.interfaces.IAnimatedHeader)
class AnimatedHeader(zeit.edit.block.Element):

    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url', zeit.content.modules.interfaces.IAnimatedHeader['url'])

    def __init__(self, context, element):
        zope.security.proxy.removeSecurityProxy(context)

    @cachedproperty
    def domain(self):
        return self.extract_domain(self.url)

    @staticmethod
    def extract_domain(url):
        if not url:
            return None
        return '.'.join(urlparse(url).netloc.split('.')[-2:])


@zope.component.adapter(zeit.content.modules.interfaces.IAnimatedHeader)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
class AnimatedHeaderXMLRepresentation:
    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        breakpoint()
        node = lxml.objectify.XML('<block/>')
        if self.context.title:
            node['title'] = self.context.title

        # Remove security proxy from lxml tree before inserting in the a
        # different tree
        node['text'] = zope.security.proxy.removeSecurityProxy(
            self.context.text)

        if self.context.caption:
            node.append(lxml.objectify.E.caption(self.context.caption))
        if self.context.is_crop_of:
            node.set('is_crop_of', self.context.is_crop_of)

        node['image'] = zope.component.getAdapter(
            self.context.image,
            zeit.cms.content.interfaces.IXMLReference, name='image')
        node['thumbnail'] = zope.component.getAdapter(
            self.context.thumbnail,
            zeit.cms.content.interfaces.IXMLReference, name='image')
        if self.context.layout:
            node.set('layout', self.context.layout)
        return node


@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(grok.Adapter):

    grok.context(zeit.content.modules.interfaces.IAnimatedHeader)

    has_thirdparty = True

    @cachedproperty
    def thirdparty_vendors(self):
        return (self.context.domain.split('.')[0],)
