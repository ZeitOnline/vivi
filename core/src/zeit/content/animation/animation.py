from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.animation.interfaces
import zeit.content.article.interfaces
import zeit.content.article.edit.interfaces
import zeit.push.interfaces
import zope.component
import zope.interface


class Animation(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing animations made from existing media."""

    zope.interface.implements(
        zeit.content.animation.interfaces.IAnimation,
        zeit.cms.interfaces.IEditorialContent,
    )

    default_template = (
        '<animation xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        "<head/><body><display_mode/><article/><images/><video/></body></animation>"
    )

    article = zeit.cms.content.reference.SingleResource(".body.article", "related")
    display_mode = zeit.cms.content.property.ObjectPathProperty('.body.display_mode')
    images = zeit.cms.content.reference.MultiResource(".body.images", "image")

    @property
    def title(self):
        return self.article.title


class AnimationType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Animation
    interface = zeit.content.animation.interfaces.IAnimation
    title = _("Animation")
    type = "animation"
