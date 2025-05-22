import grokcore.component as grok
import zope.interface
import zope.schema.interfaces

from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


@grok.implementer(zeit.wochenmarkt.interfaces.IRecipeCategory)
class RecipeCategory:
    def __init__(self, code, name, diets=None, conflicting_diets=None):
        # Conform to zeit.cms.content.sources.ObjectSource
        self.id = code
        self.title = name
        # BBB present an API a bit like zeit.cms.tagging.interfaces.ITag, even
        # though using an object here probably always has been superfluous, and
        # this could have instead been implemented with strings and the standard
        # Source value+title mechanics.
        self.code = code
        self.name = name
        self.diets = set(diets.split(',')) if diets else set()
        self.conflicting_diets = set(conflicting_diets.split(',')) if conflicting_diets else set()

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
            category = RecipeCategory(
                category_node.get('id').lower(),
                category_node.get('name'),
                category_node.get('diets'),
                category_node.get('conflicting-diets'),
            )
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

    def for_diets(self, diets):
        """Find the best matching category based on given diets."""
        possible_categories = []
        # special handling for vegetarian only, because we cannot define a diet hierachy (yet)
        # if we plan to add more, we need to setup a diet configuration
        if diets == {'vegetarian'}:
            vegetarian_only = [c for c in self._values().values() if 'vegetarian' in c.diets]
            if vegetarian_only:
                return min(
                    vegetarian_only, key=lambda category: abs(len(category.diets) - len(diets))
                )

        for category in self._values().values():
            if (
                # diets are given
                category.diets
                # given diets are at least part of category diets
                and category.diets.issubset(diets)
                # diets do not contain conflicting diets (omivore vs. vegan)
                and not category.conflicting_diets.intersection(diets)
            ):
                possible_categories.append(category)

        if not possible_categories:
            return None

        # We select the category with diet count closest to the input diets count
        return min(possible_categories, key=lambda category: abs(len(category.diets) - len(diets)))


recipeCategoriesSource = RecipeCategoriesSource()


@grok.implementer(zeit.wochenmarkt.interfaces.IIngredient)
class Ingredient:
    def __init__(self, code, **kwargs):
        self.code = code
        self.name = kwargs.get('name')
        self.qwords = (
            [x.strip() for x in kwargs.get('qwords').split(',')] if kwargs.get('qwords') else []
        )
        self.singular = kwargs.get('singular')
        self.plural = kwargs.get('plural')
        self.diet = kwargs.get('diet')
        # Conform to zeit.cms.content.sources.ObjectSource
        self.id = self.code
        self.title = self.name


class IngredientsSource(
    zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.SimpleContextualXMLSource
):
    product_configuration = 'zeit.wochenmarkt'
    config_url = 'ingredients-url'
    default_filename = 'ingredients.xml'

    @zope.interface.implementer(
        zeit.wochenmarkt.interfaces.IIngredientsSource,
        zeit.cms.content.sources.IAutocompleteSource,
    )
    class source_class(zeit.cms.content.sources.FactoredObjectSource):
        pass

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        xml = self._get_tree()
        ingredients = {}
        for ingredient_node in xml.xpath('//ingredient'):
            try:
                ingredient = Ingredient(
                    ingredient_node.get('id'),
                    name=str(ingredient_node.get('singular')).strip(),
                    qwords=ingredient_node.get('q'),
                    singular=ingredient_node.get('singular'),
                    plural=ingredient_node.get('plural').strip(),
                    diet=ingredient_node.get('diet').strip(),
                )
            except AttributeError:
                continue
            ingredients[ingredient_node.get('id')] = ingredient
        return ingredients

    def isAvailable(self, value, context):
        return True

    def search(self, term):
        term = term.lower()
        singular = {x.name.lower(): x for x in self._values().values()}

        # Ingredients that start with the term, e.g. ei -> ei, eigelb
        prefix = [value for key, value in singular.items() if key.startswith(term)]
        prefix = sorted(prefix, key=lambda x: x.name.lower())

        # Ingredients that contain the term anywhere, e.g. ei -> brei, eis
        substring = [value for key, value in singular.items() if term in key]
        substring = sorted(substring, key=lambda x: x.name.lower())

        # Put prefix matches to the top of the resultset.
        return list(dict.fromkeys(prefix + substring))

    def find(self, context, id):
        return self._values().get(id)


ingredientsSource = IngredientsSource()
