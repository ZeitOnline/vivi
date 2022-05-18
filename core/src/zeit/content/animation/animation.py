from zeit.cms.content.dav import DAVProperty
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.content.property import ObjectPathProperty, SwitchableProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.animation.interfaces import IAnimation
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.animation.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.push.interfaces
import zope.component
import zope.interface


NS = 'http://namespaces.zeit.de/CMS/animation'


@zope.interface.implementer(
    zeit.content.animation.interfaces.IAnimation,
    zeit.cms.interfaces.IAsset,
)
class Animation(zeit.cms.content.xmlsupport.XMLContentBase):
    """A type for managing animations made from existing media."""

    default_template = '<body/>'

    article = zeit.cms.content.reference.SingleResource(
        '.body.article', 'related', dav_name='article', dav_namespace=NS,
    )
    display_mode = SwitchableProperty(
        DAVProperty(IAnimation['display_mode'], NS, name='display_mode'),
        ObjectPathProperty('.body.display_mode'))

    images = zeit.cms.content.reference.MultiResource(
        '.body.image', 'image', dav_namespace=NS)
    video = zeit.cms.content.reference.SingleResource(
        '.body.video', 'related', dav_namespace=NS)

    def __getattr__(self, name):
        if name not in list(ICommonMetadata):
            raise AttributeError(name)
        return getattr(self.article, name)


class AnimationType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Animation
    interface = zeit.content.animation.interfaces.IAnimation
    title = _('Animation')
    type = 'animation'
