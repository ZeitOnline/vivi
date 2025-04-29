import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zope.interface
import zope.schema.interfaces

import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


class RecipeCategoriesSource(
    zeit.cms.content.sources.ObjectSource, zc.sourcefactory.contextual.BasicContextualSourceFactory
):
    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.content.sources.IAutocompleteSource,
    )
    class source_class(zeit.cms.content.sources.FactoredObjectSource):
        def __contains__(self, value):
            # We do not want to ask the whitelist again.
            return True

    def _values(self):
        whitelist = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        )
        return whitelist._load()

    def isAvailable(self, value, context):
        return True

    def search(self, term):
        whitelist = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        )
        return whitelist.search(term)

    def find(self, context, id):
        whitelist = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        )
        return whitelist.get(id)


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
        whitelist = zope.component.getUtility(zeit.wochenmarkt.interfaces.IIngredientsWhitelist)
        return whitelist.search(term)


ingredientsSource = IngredientsSource()
