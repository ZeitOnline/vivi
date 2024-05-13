import collections
import logging

import grokcore.component as grok
import lxml.etree
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.cli import commit_with_retry
from zeit.cms.interfaces import CONFIG_CACHE, ICMSContent
from zeit.cms.workflow.interfaces import PRIORITY_LOW, IPublish
import zeit.cms.cli
import zeit.retresco.interfaces
import zeit.wochenmarkt.interfaces


log = logging.getLogger(__name__)


def xpath_lowercase(context, x):
    return x[0].lower()


xpath_functions = lxml.etree.FunctionNamespace('zeit.ingredients')
xpath_functions['lower'] = xpath_lowercase


@grok.implementer(zeit.wochenmarkt.interfaces.IIngredient)
class Ingredient:
    def __init__(self, code, **kwargs):
        self.code = code
        self.name = kwargs.get('name')
        self.category = kwargs.get('category')
        self.qwords = kwargs.get('qwords').split(',') if kwargs.get('qwords') else None
        self.qwords_category = (
            kwargs.get('qwords_category').split(',') if kwargs.get('qwords_category') else None
        )
        self.singular = kwargs.get('singular')
        self.plural = kwargs.get('plural')
        self.diet = kwargs.get('diet')
        self.__name__ = self.code


@grok.implementer(zeit.wochenmarkt.interfaces.IIngredientsWhitelist)
class IngredientsWhitelist(grok.GlobalUtility, zeit.cms.content.sources.CachedXMLBase):
    """Search for ingredients in ingredients source"""

    product_configuration = 'zeit.wochenmarkt'
    config_url = 'ingredients-url'
    default_filename = 'ingredients.xml'

    @property
    def data(self):
        return self._load()

    def search(self, term):
        xml = self._get_tree()
        # Get ingredients that start with the term, e.g. ei -> ei, eigelb and
        # sort alphabethically
        exact_matches = xml.xpath(
            ('//ingredient[starts-with(' 'zeit:lower(@singular), "{0}")]').format(term.lower()),
            namespaces={'zeit': 'zeit.ingredients'},
        )
        exact_matches = sorted(exact_matches, key=lambda x: x.get('singular').lower())

        # Get ingredients that contain the search term as part of a an
        # ingredient, e.g. ei -> brei, eis and sort alphabetically
        fuzzy_matches = xml.xpath(
            (
                '//ingredient[contains(zeit:lower(@singular), "{0}")'
                'and not(starts-with(zeit:lower(@singular), "{0}"))]'
            ).format(term.lower()),
            namespaces={'zeit': 'zeit.ingredients'},
        )
        fuzzy_matches = sorted(fuzzy_matches, key=lambda x: x.get('singular').lower())

        # Put exact matches to the top of the resultset.
        matches = exact_matches + fuzzy_matches

        return [self.get(x.get('id')) for x in matches]

    def category(self, category, term=''):
        return [
            ingredient
            for ingredient in self.search(term)
            if getattr(ingredient, 'category', None) == category
        ]

    def get(self, code):
        return self.data.get(code)

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        xml = self._get_tree()
        ingredients = collections.OrderedDict()
        for ingredient_node in xml.xpath('//ingredient'):
            try:
                ingredient = Ingredient(
                    ingredient_node.get('id'),
                    name=str(ingredient_node.get('singular')).strip(),
                    category=ingredient_node.getparent().tag,
                    qwords=ingredient_node.get('q'),
                    qwords_category=ingredient_node.getparent().get('q'),
                    singular=ingredient_node.get('singular'),
                    plural=ingredient_node.get('plural').strip(),
                    diet=ingredient_node.get('diet'),
                )
            except AttributeError:
                continue
            ingredients[ingredient_node.get('id')] = ingredient
        log.info('Ingredients loaded.')
        return ingredients

    def collect_used(self):
        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        result = es.aggregate(
            {
                'aggs': {
                    'ingredients': {'terms': {'field': 'payload.recipe.ingredients', 'size': 10000}}
                },
                'size': 0,
            }
        )
        used = set()
        for item in result['ingredients']['buckets']:
            used.add(item['key'])

        xml = self._get_tree()
        for item in xml.xpath('//ingredient'):
            if item.get('id') not in used:
                item.getparent().remove(item)
        return xml


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.wochenmarkt', 'used-ingredients-principal')
)
def collect_used():
    ingredients = zope.component.getUtility(zeit.wochenmarkt.interfaces.IIngredientsWhitelist)
    used = ingredients.collect_used()

    for _ in commit_with_retry():
        source = ICMSContent('http://xml.zeit.de/data/ingredients_in_use.xml')
        with checked_out(source) as co:
            co.xml = used

    IPublish(source).publish(priority=PRIORITY_LOW)
