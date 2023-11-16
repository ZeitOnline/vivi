from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import ICardstackBlock
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(ICardstackBlock)
class CardstackBlock(zeit.content.cp.blocks.block.Block):
    type = 'cardstack'

    card_id = ObjectPathAttributeProperty('.', 'card_id', ICardstackBlock['card_id'])
    is_advertorial = ObjectPathAttributeProperty(
        '.', 'is_advertorial', ICardstackBlock['is_advertorial']
    )

    cardstack_background_color = ObjectPathAttributeProperty(
        '.', 'cardstack_background_color', ICardstackBlock['cardstack_background_color']
    )


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = CardstackBlock
    title = _('Cardstack block')
