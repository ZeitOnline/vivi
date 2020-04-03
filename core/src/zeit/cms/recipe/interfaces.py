import zope.interface

class IIngredients(zope.interface.Interface):
    """Maker interface for ingredients."""

    def search(term):
        """Return a list of ingredients whose names contain the given term."""

    def category(category, term):
        """Return a list of ingredients from a category contain given term."""

    def get(id):
        """Return the ingredient for the given id."""
