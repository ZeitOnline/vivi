import grokcore.component as grok
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zope.interface
import zope.schema.interfaces

from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


@grok.implementer(zeit.wochenmarkt.interfaces.IRecipeCategory)
class RecipeCategory:
    def __init__(self, code, name):
        # Conform to zeit.cms.content.sources.ObjectSource
        self.id = code
        self.title = name
        # BBB present an API a bit like zeit.cms.tagging.interfaces.ITag, even
        # though using an object here probably always has been superfluous, and
        # this could have instead been implemented with strings and the standard
        # Source value+title mechanics.
        self.code = code
        self.name = name

    @classmethod
    def from_xml(cls, node):
        return recipeCategoriesSource(None).find(node.get('code'))

    def __eq__(self, other):
        if not zeit.wochenmarkt.interfaces.IRecipeCategory.providedBy(other):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


class RecipeCategoriesSource(
    zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.SimpleContextualXMLSource
):
    product_configuration = 'zeit.wochenmarkt'
    config_url = 'categories-url'
    default_filename = 'categories.xml'

    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.content.sources.IAutocompleteSource,
    )
    class source_class(zeit.cms.content.sources.FactoredObjectSource):
        pass

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        xml = self._get_tree()
        categories = {}
        for category_node in xml.xpath('//category'):
            category = RecipeCategory(category_node.get('id').lower(), category_node.get('name'))
            categories[category_node.get('id')] = category
        return categories

    def isAvailable(self, value, context):
        return True

    def search(self, term):
        term = term.lower()
        titles = {x.name.lower(): x for x in self._values().values()}
        return [value for key, value in titles.items() if term in key]

    def find(self, context, id):
        return self._values().get(id)


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
