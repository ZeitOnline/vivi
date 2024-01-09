import collections
import logging

from lxml.objectify import E
import grokcore.component as grok
import lxml.etree
import zope.interface

from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.sources
import zeit.wochenmarkt.interfaces


log = logging.getLogger(__name__)


def xpath_lowercase(context, x):
    return x[0].lower()


xpath_functions = lxml.etree.FunctionNamespace('zeit.categories')
xpath_functions['lower'] = xpath_lowercase


@grok.implementer(zeit.wochenmarkt.interfaces.IRecipeCategory)
class RecipeCategory:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.__name__ = self.code

    @classmethod
    def from_xml(cls, node):
        code = node.get('code')
        try:
            name = (
                zope.component.getUtility(zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist)
                .get(code)
                .name
            )
        except AttributeError:
            # Take care of insufficient whitelist data e.g. missing entries.
            return None
        return cls(code, name)


class RecipeCategories:
    """Property which stores recipe categories in DAV."""

    def __get__(self, instance, class_):
        if instance is not None:
            categories = [
                RecipeCategory.from_xml(x)
                for x in (instance.xml.xpath('./head/recipe_categories/category'))
            ]
            return tuple(c for c in categories if c is not None)
        return None

    def __set__(self, instance, value):
        recipe_categories = instance.xml.xpath('./head/recipe_categories')
        if len(recipe_categories) != 0:
            instance.xml.head.remove(recipe_categories[0])
        value = self._remove_duplicates(value)
        if len(value) > 0:
            el = E.recipe_categories()
            for item in value:
                el.append(E.category(code=item.code))
            instance.xml.head.append(el)

    def _remove_duplicates(self, categories):
        result = collections.OrderedDict()
        for category in categories:
            if category.code not in result:
                result[category.code] = category
        return result.values()


@grok.implementer(zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist)
class RecipeCategoriesWhitelist(grok.GlobalUtility, zeit.cms.content.sources.CachedXMLBase):
    """Search for categories in categories source"""

    product_configuration = 'zeit.wochenmarkt'
    config_url = 'categories-url'
    default_filename = 'categories.xml'

    @property
    def data(self):
        return self._load()

    def search(self, term):
        xml = self._get_tree()
        nodes = xml.xpath(
            '//category[contains(zeit:lower(@name), "%s")]' % term.lower(),
            namespaces={'zeit': 'zeit.categories'},
        )
        return [self.get(x.get('id')) for x in nodes]

    def get(self, code):
        result = self.data.get(code)
        return result if result else None

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        xml = self._get_tree()
        categories = collections.OrderedDict()
        for category_node in xml.xpath('//category'):
            category = RecipeCategory(category_node.get('id'), category_node.get('name'))
            categories[category_node.get('id')] = category
        log.info('categories loaded.')
        return categories
