from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class RawTextBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IRawTextBlock)

    text_reference = zeit.cms.content.reference.SingleResource(
        '.text_reference', 'related')
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text', zeit.content.cp.interfaces.IRawTextBlock['text'])

    @property
    def raw_code(self):
        if self.text_reference:
            return self.text_reference.text

        if self.text:
            return self.text

        return ''


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'rawtext', _('raw text block'))
