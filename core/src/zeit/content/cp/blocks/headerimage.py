from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class HeaderImageBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IHeaderImageBlock)

    image = zeit.cms.content.property.SingleResource('.image')


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'headerimage', _('Header image block'))
