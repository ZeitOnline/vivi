from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.ICitationComment)
class CitationComment(zeit.content.article.edit.block.Block):
    type = 'citation_comment'

    text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ICitationComment['text']
    )
    url = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'url')
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zeit.content.article.edit.interfaces.ICitationComment['layout']
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = CitationComment
    title = _('Citation Comment')
