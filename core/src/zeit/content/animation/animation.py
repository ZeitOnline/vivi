import grokcore.component as grok
import zope.component
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.interfaces import IArticle
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.animation.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.audio.interfaces


@zope.interface.implementer(
    zeit.content.animation.interfaces.IAnimation,
    zeit.cms.interfaces.IAsset,
)
class Animation(zeit.cms.content.xmlsupport.XMLContentBase):
    """A type for managing animations made from existing media."""

    default_template = '<body/>'

    article = zeit.cms.content.reference.SingleResource('.body.article', 'related')
    display_mode = zeit.cms.content.property.ObjectPathProperty('.body.display_mode')
    images = zeit.cms.content.reference.MultiResource('.body.image', 'image')
    video = zeit.cms.content.reference.SingleResource('.body.video', 'related')
    gallery = zeit.cms.content.reference.SingleResource('.body.gallery', 'related')

    _proxy_attributes = frozenset(list(IArticle))

    def __getattr__(self, name):
        if name not in self._proxy_attributes:
            raise AttributeError(name)
        if self.article is None:  # Conform to interface, even if reference is broken
            return IArticle[name].default
        return getattr(self.article, name)


class AnimationType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Animation
    interface = zeit.content.animation.interfaces.IAnimation
    title = _('Animation')
    type = 'animation'


@grok.adapter(zeit.content.animation.interfaces.IAnimation)
@grok.implementer(zeit.content.image.interfaces.IImages)
def animation_images(context):
    return zeit.content.image.interfaces.IImages(context.article)


@grok.adapter(zeit.content.animation.interfaces.IAnimation)
@grok.implementer(zeit.content.audio.interfaces.IAudioReferences)
def animation_audios(context):
    return zeit.content.audio.interfaces.IAudioReferences(context.article)


@grok.adapter(zeit.content.animation.interfaces.IAnimation)
@grok.implementer(zeit.content.article.interfaces.ISpeechbertChecksum)
def animation_checksum(context):
    return zeit.content.article.interfaces.ISpeechbertChecksum(context.article)
