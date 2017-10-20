import zeit.cms.content.reference
import zeit.edit.block
import zope.interface


class RawText(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IRawText)

    text_reference = zeit.cms.content.reference.SingleResource(
        '.text_reference', 'related')
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text', zeit.content.modules.interfaces.IRawText['text'])

    @property
    def raw_code(self):
        if self.text_reference:
            return self.text_reference.text
        if self.text:
            return self.text
        return ''
