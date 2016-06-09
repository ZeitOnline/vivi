from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.reference
import grokcore.component
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class RawText(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IRawText)
    type = 'rawtext'
    text_reference = zeit.cms.content.reference.SingleResource(
        '.text_reference', 'related')
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text',
        zeit.content.article.edit.interfaces.IRawText['text'])

    @property
    def raw_code(self):
        if self.text_reference:
            return self.text_reference.text

        if self.text:
            return self.text

        return ''


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = RawText
    title = _('Raw text block')
