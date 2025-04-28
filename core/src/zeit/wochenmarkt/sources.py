import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zope.interface
import zope.schema.interfaces

import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


class RecipeCategoriesSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.content.sources.IAutocompleteSource,
    )
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def __contains__(self, value):
            # We do not want to ask the whitelist again.
            return True

    def search(self, term):
        from zeit.wochenmarkt.interfaces import IRecipeCategoriesWhitelist

        categories = zope.component.getUtility(IRecipeCategoriesWhitelist)
        return categories.search(term)

    def getTitle(self, context, value):
        return value.name

    def getToken(self, context, value):
        return value.code


recipeCategoriesSource = RecipeCategoriesSource()


class IngredientsSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IIngredientsSource,
        zeit.cms.content.sources.IAutocompleteSource,
    )
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def __contains__(self, value):
            # We do not want to ask the whitelist again.
            return True

    def search(self, term):
        from zeit.wochenmarkt.interfaces import IIngredientsWhitelist

        ingredients = zope.component.getUtility(IIngredientsWhitelist)
        return ingredients.search(term)


ingredientsSource = IngredientsSource()
