import grokcore.component as grok
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.wochenmarkt.sources import ingredientsSource, recipeCategoriesSource
import zeit.cms.checkout.interfaces
import zeit.content.article.interfaces


class IRecipeArticle(zope.interface.Interface):
    categories = zope.schema.Tuple(
        title=_('Recipe Categories'),
        value_type=zope.schema.Choice(source=recipeCategoriesSource),
        default=(),
        required=False,
    )

    titles = zope.schema.Tuple(
        title=_('Recipe Titles'),
        value_type=zope.schema.TextLine(),
        default=(),
        required=False,
    )

    ingredients = zope.schema.Tuple(
        title=_('Recipe Ingredients'),
        value_type=zope.schema.TextLine(),
        default=(),
        required=False,
    )


@grok.implementer(IRecipeArticle)
class RecipeArticle(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.context(zeit.content.article.interfaces.IArticle)

    zeit.cms.content.dav.mapProperties(
        IRecipeArticle,
        'http://namespaces.zeit.de/CMS/recipe',
        ('ingredients', 'titles'),
        use_default=True,
    )

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        if not value:  # XXX kludgy, revisit with WCM-601
            self._categories = None
        else:
            value = list(dict.fromkeys(value))  # ordered set()
            self._categories = value

    _categories = zeit.cms.content.dav.DAVProperty(
        IRecipeArticle['categories'],
        'http://namespaces.zeit.de/CMS/recipe',
        'categories',
        use_default=True,
    )


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_recipes_of_article(context, event):
    source = zeit.wochenmarkt.sources.recipeCategoriesSource(context)
    if context.genre not in source.factory.genres:
        return
    recipes = context.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
    titles = [context.title]
    ingredients = set()

    info = IRecipeArticle(context)
    categories = list(info.categories)
    for recipe in recipes:
        if recipe.title:
            titles.append(recipe.title)
        ingredients = ingredients | {x.id for x in recipe.ingredients}

        if complexity := source.find(f'complexity-{recipe.complexity}'):
            categories.append(complexity)
        if time := source.find(f'time-{recipe.time}'):
            categories.append(time)
    # Only guess diet categories once, so the user can remove them.
    if not info.titles and (category := _categorize_by_ingredients_diet(ingredients)):
        categories.append(category)

    info.titles = titles or None  # XXX kludgy, revisit with WCM-601
    info.ingredients = ingredients or None
    info.categories = categories


def _categorize_by_ingredients_diet(ingredients):
    source = ingredientsSource(None)
    diets = {source.find(i).diet for i in ingredients}
    return recipeCategoriesSource(None).factory.for_diets(diets)
