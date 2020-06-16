from zeit.cms.interfaces import CONFIG_CACHE
import collections
import gocept.lxml.objectify
import grokcore.component as grok
import logging
import lxml.etree
import six
import zeit.wochenmarkt.interfaces
import zope.component
import zope.component.hooks


log = logging.getLogger(__name__)


def xpath_lowercase(context, x):
    return x[0].lower()


xpath_functions = lxml.etree.FunctionNamespace('zeit.ingredients')
xpath_functions['lower'] = xpath_lowercase


@grok.implementer(zeit.wochenmarkt.interfaces.IIngredient)
class Ingredient(object):

    def __init__(self, code, name, category):
        self.code = code
        self.name = name
        self.category = category
        self.__name__ = self.code


@grok.implementer(zeit.wochenmarkt.interfaces.IIngredientsWhitelist)
class IngredientsWhitelist(grok.GlobalUtility):
    """Search for ingredients in ingredients source"""

    @property
    def data(self):
        return self._load()

    def search(self, term):
        xml = self._fetch()
        nodes = xml.xpath(
            '//ingredient[contains(zeit:lower(@singular), "%s")]' %
            term.lower(), namespaces={'zeit': 'zeit.ingredients'})
        return [self.get(x.get('id')) for x in nodes]

    def category(self, category, term=''):
        return [
            ingredient for ingredient in self.search(term)
            if ingredient.category == category]

    def get(self, code):
        result = self.data.get(code)
        return result if result else None

    @CONFIG_CACHE.cache_on_arguments()
    def _fetch(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.wochenmarkt')
        url = config.get('ingredients-url')
        log.info('Loading ingredients from %s', url)
        data = six.moves.urllib.request.urlopen(url)
        return gocept.lxml.objectify.fromfile(data)

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        xml = self._fetch()
        ingredients = collections.OrderedDict()
        for ingredient_node in xml.xpath('//ingredient'):
            ingredient = Ingredient(
                ingredient_node.get('id'),
                six.text_type(ingredient_node.get('singular')).strip(),
                category=ingredient_node.getparent().tag)
            ingredients[ingredient_node.get('id')] = ingredient
        log.info('Ingredients loaded.')
        return ingredients
