from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import ICardstack
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Cardstack(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(ICardstack)
    type = 'cardstack'

    card_id = ObjectPathAttributeProperty(
        '.', 'card_id', ICardstack['card_id'])
    is_advertorial = ObjectPathAttributeProperty(
        '.', 'is_advertorial', ICardstack['is_advertorial'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Cardstack
    title = _('Cardstack block')
