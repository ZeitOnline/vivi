from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
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


@zope.interface.implementer(
    zeit.content.animation.interfaces.IAnimation,
    zeit.cms.interfaces.IAsset,
)
class Animation(zeit.cms.content.xmlsupport.XMLContentBase):
    """A type for managing animations made from existing media."""

    default_template = "<body/>"

    article = zeit.cms.content.reference.SingleResource(
        ".body.article", "related"
    )
    display_mode = zeit.cms.content.property.ObjectPathProperty(
        ".body.display_mode"
    )
    images = zeit.cms.content.reference.MultiResource(".body.image", "image")
    video = zeit.cms.content.reference.SingleResource(".body.video", "related")
    gallery = zeit.cms.content.reference.SingleResource(
        ".body.gallery", "related")

    _proxy_attributes = frozenset(list(ICommonMetadata) + ['genre'])

    def __getattr__(self, name):
        if name not in self._proxy_attributes:
            raise AttributeError(name)
        return getattr(self.article, name)


class AnimationType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Animation
    interface = zeit.content.animation.interfaces.IAnimation
    title = _("Animation")
    type = "animation"
