import zope.interface
import zope.schema


class IIngredients(zope.interface.Interface):
    """Marker interface for ingredients."""

    def search(term):
        """Return a list of ingredients whose names contain the given term."""

    def category(category, term):
        """Return a list of ingredients from a category contain given term."""

    def get(id):
        """Return the ingredient for the given id."""


class IIngredientsSource(zope.schema.interfaces.IIterableSource):
    """Available ingredients."""


class IIngredient(zope.interface.Interface):
    """An ingredient item in a list of IIngredients as part of
    IIngredientSource.
    """

    code = zope.schema.TextLine(
        title=u'Internal ingredient id')

    name = zope.schema.TextLine(
        title=u'User visible name of ingredient')

    category = zope.schema.TextLine(
        title=u'The kind of category this ingredient belongs to')
