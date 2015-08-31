from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import ICardstackBlock
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class CardstackBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(ICardstackBlock)

    card_id = ObjectPathAttributeProperty(
        '.', 'card_id', ICardstackBlock['card_id'])
    is_advertorial = ObjectPathAttributeProperty(
        '.', 'is_advertorial', ICardstackBlock['is_advertorial'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'cardstack', _('Cardstack block'))
