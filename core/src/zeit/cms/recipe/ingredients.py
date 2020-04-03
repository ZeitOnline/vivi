import collections
import gocept.lxml.objectify
import grokcore.component as grok
import logging
import lxml.etree
import urllib2
import zeit.cms.recipe.interfaces
import zope.component


log = logging.getLogger(__name__)


def xpath_lowercase(context, x):
    return x[0].lower()
xpath_functions = lxml.etree.FunctionNamespace('zeit.ingredients')
xpath_functions['lower'] = xpath_lowercase



class Ingredient(object):

    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category
        self.__name__ = self.name


@grok.implementer(zeit.cms.recipe.interfaces.IIngredients)
class Ingredients(grok.GlobalUtility):
    """Search for ingredients in ingredients.xml"""

    @property
    def data(self):
        return self._load()

    def search(self, term):
        xml = self._fetch()
        nodes = xml.xpath(
            '//ingredient[contains(zeit:lower(text()), "%s")]' %
            term.lower(), namespaces={'zeit': 'zeit.ingredients'})
        return [self.get(x.get('id')) for x in nodes]

    def category(self, category, term=''):
        return [
            ingredient for ingredient in self.search(term)
            if ingredient.category == category]

    def get(self, id):
        result = self.data.get(id)
        return result if result else None

    def _fetch(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        url = config.get('ingredients-url')
        log.info('Loading ingredients from %s', url)
        data = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(data)

    def _load(self):
        xml = self._fetch()
        ingredients = collections.OrderedDict()
        for ingredient_node in xml.xpath('//ingredient'):
            #import pdb; pdb.set_trace()
            ingredient = Ingredient(
                ingredient_node.get('id'),
                unicode(ingredient_node).strip(),
                category=ingredient_node.getparent().tag)
            ingredients[ingredient_node.get('id')] = ingredient
        log.info('Ingredients loaded.')
        return ingredients
