from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class MarkupBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IMarkupBlock)

    text = zeit.cms.content.property.Structure('.text')
    alignment = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'align', zeit.content.cp.interfaces.IMarkupBlock['alignment'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'markup', _('Markup block'))
