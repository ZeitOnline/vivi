import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.reference
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.author.interfaces


class ReferenceProperty(zeit.cms.content.reference.SingleReferenceProperty):
    def __set__(self, instance, value):
        saved_attributes = {
            name: getattr(instance, name)
            for name in [
                '__name__',
            ]
        }

        super().__set__(instance, value)

        for name, val in saved_attributes.items():
            setattr(instance, name, val)
        instance._p_changed = True


@grok.implementer(zeit.content.article.edit.interfaces.IAuthor)
class Author(zeit.content.article.edit.reference.Reference):
    type = 'author'

    references = ReferenceProperty('.', 'related')


class Factory(zeit.content.article.edit.reference.ReferenceFactory):
    produces = Author
    title = _('Author block')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea, zeit.content.author.interfaces.IAuthor, int
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_author_block_from_author(body, content, position):
    block = Factory(body)(position)
    block.references = block.references.get(content) or block.references.create(content)
    return block
