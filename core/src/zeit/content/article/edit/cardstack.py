from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Cardstack(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grok.implements(zeit.content.article.edit.interfaces.ICardstack)
    type = 'cardstack'

    card_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'card_id',
        zeit.content.article.edit.interfaces.ICardstack['card_id'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Cardstack
    title = _('Cardstack')
