import zope.interface
import zope.schema


class IRecipeCategory(zope.interface.Interface):
    """A recipe category item in a list of IRecipeCategories as part of
    IRecipeCategorySource.
    """

    code = zope.schema.TextLine(title='Internal recipe category id')
    name = zope.schema.TextLine(title='User visible name of recipe category')
    # XXX Figure out which of these APIs we actually want.
    id = code
    title = name
    flag = zope.schema.TextLine(title='Flag of recipe category, to identify special categories')


class IRecipeCategoriesSource(zope.schema.interfaces.IIterableSource):
    """Available categories."""


class IIngredient(zope.interface.Interface):
    """An ingredient item in a list of IIngredients as part of
    IIngredientSource.
    """

    code = zope.schema.TextLine(title='Internal ingredient id')
    name = zope.schema.TextLine(title='User visible name of ingredient')
    # XXX Figure out which of these APIs we actually want.
    id = code
    title = name

    qwords = zope.schema.List(zope.schema.TextLine())
    singular = zope.schema.TextLine()
    plural = zope.schema.TextLine()


class IIngredientsSource(zope.schema.interfaces.IIterableSource):
    """Available ingredients."""
