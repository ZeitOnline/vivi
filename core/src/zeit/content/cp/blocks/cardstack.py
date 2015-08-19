from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class CardstackBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.ICardstackBlock)

    card_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'card_id',
        zeit.content.cp.interfaces.ICardstackBlock['card_id'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'cardstack', _('Cardstack block'))
