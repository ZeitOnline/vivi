import collections
import importlib.resources

import zeit.cms.testing
import zeit.wochenmarkt.categories
import zeit.wochenmarkt.ingredients


product_config = """\
<product-config zeit.wochenmarkt>
  categories-url file://{here}/tests/fixtures/categories.xml
  ingredients-url file://{here}/tests/fixtures/ingredients.xml
</product-config>
""".format(here=importlib.resources.files(__package__))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cms.testing.CONFIG_LAYER,)
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class RecipeCategoriesHelper:
    """Mixin for tests which need some recipe category infrastrucutre."""

    def get_category(self, code):
        category = zeit.wochenmarkt.categories.RecipeCategory(code=code, name='_' + code)
        return category

    def setup_categories(self, *codes):
        categories = collections.OrderedDict()
        for code in codes:
            categories[code] = self.get_category(code)
        return categories
