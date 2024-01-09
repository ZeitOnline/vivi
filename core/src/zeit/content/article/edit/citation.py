import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.ICitation)
class Citation(zeit.content.article.edit.block.Block):
    type = 'citation'

    text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ICitation['text']
    )
    attribution = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'attribution', zeit.content.article.edit.interfaces.ICitation['attribution']
    )
    url = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'url')
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zeit.content.article.edit.interfaces.ICitation['layout']
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Citation
    title = _('Citation')
