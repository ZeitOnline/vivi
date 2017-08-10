from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Citation(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.ICitation)
    type = 'citation'

    text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ICitation['text'])
    attribution = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'attribution',
        zeit.content.article.edit.interfaces.ICitation['attribution'])
    url = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'url')
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout',
        zeit.content.article.edit.interfaces.ICitation['layout'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Citation
    title = _('Citation')


# Could be defined as an Adapter (IArticle -> ICitation) as well
# Im not sure, when to use just a function or an Adapter
def find_first_citation(article):
    body = zeit.content.article.edit.interfaces.IEditableBody(article, None)
    if not body:
        return None
    for element in body.values():
        if zeit.content.article.edit.interfaces.ICitation.providedBy(element):
            return zeit.content.article.edit.interfaces.ICitation(
                element)
    return None
