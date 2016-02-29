from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.container.interfaces
import zope.interface


class RawTextBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IRawTextBlock)

    text_reference = zeit.cms.content.reference.SingleResource(
        '.text_reference','related')
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text', zeit.content.cp.interfaces.IRawTextBlock['text'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'rawtext', _('raw text block'))

