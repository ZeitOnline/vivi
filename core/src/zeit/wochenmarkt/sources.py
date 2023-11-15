import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.contentsource
import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces
import zope.interface
import zope.schema.interfaces


class RecipeCategoriesSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    check_interfaces = zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
    name = 'categories'
    addform = 'zeit.wochenmarkt.add_contextfree'

    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.content.contentsource.IAutocompleteSource,
    )
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def get_check_types(self):
            """IAutocompleteSource, but not applicable for us"""
            return []

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
    check_interfaces = zeit.wochenmarkt.interfaces.IIngredientsWhitelist
    name = 'ingredients'
    addform = 'zeit.wochenmarkt.add_contextfree'

    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IIngredientsSource,
        zeit.cms.content.contentsource.IAutocompleteSource,
    )
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def get_check_types(self):
            """IAutocompleteSource, but not applicable for us"""
            return []

        def __contains__(self, value):
            # We do not want to ask the whitelist again.
            return True

    def search(self, term):
        from zeit.wochenmarkt.interfaces import IIngredientsWhitelist

        ingredients = zope.component.getUtility(IIngredientsWhitelist)
        return ingredients.search(term)


ingredientsSource = IngredientsSource()
