from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.cook.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.push.interfaces
import zope.component
import zope.interface
import zeit.content.author.author


@zope.interface.implementer(
    zeit.content.cook.interfaces.ICook,
    zeit.cms.interfaces.IEditorialContent,
)
class Cook(zeit.content.author.author.Author):
    pass


class CookType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Cook
    interface = zeit.content.cook.interfaces.ICook
    title = _("Cook")
    type = "cook"
