import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.recipelist


@grok.implementer(zeit.content.article.edit.interfaces.IRecipeList)
class RecipeList(zeit.content.modules.recipelist.RecipeList, zeit.content.article.edit.block.Block):
    type = 'recipelist'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = RecipeList
    title = _('Recipe list block')
