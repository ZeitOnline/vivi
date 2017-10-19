from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.rawtext
import zeit.edit.block
import zope.interface


class RawTextBlock(
        zeit.content.modules.rawtext.RawText,
        zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IRawTextBlock)


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'rawtext', _('raw text block'))
