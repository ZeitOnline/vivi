import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IIngredientDice
import zeit.content.article.edit.block


@grok.implementer(IIngredientDice)
class IngredientDice(zeit.content.article.edit.block.Block):
    type = 'ingredientdice'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = IngredientDice
    title = _('Ingredient dice block')
