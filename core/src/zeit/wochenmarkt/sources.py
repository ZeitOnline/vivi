import grokcore.component as grok
import zope.interface
import zope.schema.interfaces

from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.config
import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


@grok.implementer(zeit.wochenmarkt.interfaces.IRecipeCategory)
class RecipeCategory:
    def __init__(self, code, name, flag=None):
        # Conform to zeit.cms.content.sources.ObjectSource
        self.id = code
        self.title = name
        self.flag = flag
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
            category = RecipeCategory(
                category_node.get('id').lower(),
                category_node.get('name'),
                category_node.get('flag'),
            )
            categories[category_node.get('id')] = category
        return categories

    def isAvailable(self, value, context):
        return True

    @property
    def genres(self):
        return zeit.cms.config.get('zeit.wochenmarkt', 'recipe-genres', '').split(',')

    def search(self, term, flag='no-search'):
        term = term.lower()
        categories = []
        for category in self._values().values():
            if flag is not None and category.flag == flag:
                continue
            if term in category.name.lower():
                categories.append(category)
        return categories

    def prefix_match(self, term, count=None):
        term = term.lower()
        result = []
        for value in self._values().values():
            if value.flag != 'no-search' and value.name.lower().startswith(term):
                result.append(value)
                if count and len(result) >= count:
                    break
        return result

    def find(self, context, id):
        return self._values().get(id)

    DIETS = {  # We require these IDs to exist in categories.xml
        'vegan': 'vegane-rezepte',
        'vegetarian': 'vegetarische-rezepte',
    }

    def for_diets(self, diets):
        if diets == {'vegan'}:
            return self.find(None, self.DIETS['vegan'])
        elif diets == {'vegan', 'vegetarian'} or diets == {'vegetarian'}:
            return self.find(None, self.DIETS['vegetarian'])
        return None


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

        # Ingredients that start with the term, e.g. ei -> ei, eigelb
        prefix = []
        # Ingredients that contain the term anywhere, e.g. ei -> brei, eis
        substring = []
        for value in self._values().values():
            name = value.name.lower()
            if name.startswith(term):
                prefix.append(value)
            elif term in name:
                substring.append(value)
        prefix = sorted(prefix, key=lambda x: x.name.lower())
        substring = sorted(substring, key=lambda x: x.name.lower())

        # Put prefix matches to the top of the resultset.
        return list(dict.fromkeys(prefix + substring))

    def prefix_match(self, term, count=None):
        term = term.lower()
        result = []
        for value in self._values().values():
            if value.name.lower().startswith(term):
                result.append(value)
                if count and len(result) >= count:
                    break
        return result

    def search_qwords(self, term):
        term = term.lower()
        result = []
        for value in self._values().values():
            for q in value.qwords:
                if q.lower().startswith(term):
                    result.append(value)
        return result

    def find(self, context, id):
        return self._values().get(id)


ingredientsSource = IngredientsSource()
