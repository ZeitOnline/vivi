import grokcore.component as grok
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.block
import zeit.edit.interfaces


@grok.adapter(zeit.content.article.edit.interfaces.IElement)
@grok.implementer(zeit.content.article.interfaces.IArticle)
def article_for_element(context):
    return zeit.content.article.interfaces.IArticle(context.__parent__, None)


class Block(zeit.edit.block.SimpleElement):
    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.baseclass()


class BlockFactory(zeit.edit.block.ElementFactory):
    grok.baseclass()
    grok.context(zeit.content.article.edit.interfaces.IArticleArea)
    # No title so we are excluded from @@block-factories -- our blocks are
    # created via the toolbar, and should not appear in the module library.
    title = None

    def get_xml(self):
        return getattr(lxml.objectify.E, self.element_type)()
