import zope.interface
import zope.schema


class IRecipeCategory(zope.interface.Interface):
    """A recipe category item in a list of IRecipeCategories as part of
    IRecipeCategorySource.
    """

    code = zope.schema.TextLine(title='Internal recipe category id')

    name = zope.schema.TextLine(title='User visible name of recipe category')


class IRecipeCategoriesSource(zope.schema.interfaces.IIterableSource):
    """Available categories."""


class IIngredient(zope.interface.Interface):
    """An ingredient item in a list of IIngredients as part of
    IIngredientSource.
    """

    code = zope.schema.TextLine(title='Internal ingredient id')

    name = zope.schema.TextLine(title='User visible name of ingredient')


class IIngredientsSource(zope.schema.interfaces.IIterableSource):
    """Available ingredients."""
