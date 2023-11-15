from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok

import zeit.content.article.edit.block
from zeit.content.article.edit.interfaces import IIngredientDice


@grok.implementer(IIngredientDice)
class IngredientDice(zeit.content.article.edit.block.Block):
    type = 'ingredientdice'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = IngredientDice
    title = _('Ingredient dice block')
