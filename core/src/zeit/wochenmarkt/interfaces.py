import zope.interface
import zope.schema


class IRecipeCategoriesWhitelist(zope.interface.Interface):
    """The whitelist contains all selectable recipe categories providing
    `IRecipeCategory`.
    """

    def search(term):
        """Return a list of categories whose names contain the given term."""

    def get(id):
        """Return the category for the given id."""


class IRecipeCategory(zope.interface.Interface):
    """A recipe category item in a list of IRecipeCategories as part of
    IRecipeCategorySource.
    """

    code = zope.schema.TextLine(title='Internal recipe category id')

    name = zope.schema.TextLine(title='User visible name of recipe category')


class IRecipeCategoriesSource(zope.schema.interfaces.IIterableSource):
    """Available categories."""


class IIngredientsWhitelist(zope.interface.Interface):
    """The whitelist contains all selectable ingredients providing
    `IIngredient`.
    """

    def search(term):
        """Return a list of ingredients whose names contain the given term."""

    def category(category, term):
        """Return a list of ingredients from a category contain given term."""

    def qwords(id):
        """Returns a list of query words for an ingredient id."""

    def qwords_category(id):
        """Returns a list of query words for an ingredients category."""

    def singular(id):
        """Returns the singular for an ingredient id."""

    def plural(id):
        """Returns the plural for an ingredient id."""

    def diet(id):
        """Returns a list of diet types for an ingredient id."""

    def get(id):
        """Return the ingredient for the given id."""


class IIngredientsSource(zope.schema.interfaces.IIterableSource):
    """Available ingredients."""


class IIngredient(zope.interface.Interface):
    """An ingredient item in a list of IIngredients as part of
    IIngredientSource.
    """

    code = zope.schema.TextLine(title='Internal ingredient id')

    name = zope.schema.TextLine(title='User visible name of ingredient')

    category = zope.schema.TextLine(title='The kind of category this ingredient belongs to')
