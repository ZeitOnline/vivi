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


class ArticleReferenceProperty(zeit.cms.content.reference.SingleResource):

    ATTRIBUTES = set(["__name__"]) | set(['display_mode', 'article'])

    def __set__(self, instance, value):
        saved_attributes = {name: getattr(instance, name) for name in self.ATTRIBUTES}

        super(ArticleReferenceProperty, self).__set__(instance, value)

        for name, val in saved_attributes.items():
            setattr(instance, name, val)
        instance.is_empty = value is None
        instance._p_changed = True


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

    article = ArticleReferenceProperty(".", "article")
    display_mode = zeit.cms.content.property.ObjectPathProperty('.body.display_mode')

    @property
    def title(self):
        return u"Foo"


class AnimationType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Animation
    interface = zeit.content.animation.interfaces.IAnimation
    title = _("Animation")
    type = "animation"
