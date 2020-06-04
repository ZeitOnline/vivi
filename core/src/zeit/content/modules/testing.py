import collections
import pkg_resources
import zeit.cmp.testing
import zeit.cms.content.add
import zeit.cms.testing
import zeit.content.modules
import zeit.content.text.text
import zeit.wochenmarkt.ingredients


product_config = """\
<product-config zeit.content.modules>
  jobticker-source file://{base}/tests/fixtures/jobticker.xml
  subject-source file://{base}/tests/fixtures/mail-subjects.xml
  embed-provider-source file://{base}/tests/fixtures/embed-providers.xml
  newsletter-source file://{base}/tests/fixtures/newsletter.xml
  recipe-metadata-source file://{base}/tests/fixtures/recipe-metadata.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, '.'))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cmp.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class IngredientsHelper(object):
    """Mixin for tests which need some ingredients infrastrucutre."""

    def get_ingredient(self, code):
        ingredient = zeit.content.modules.recipelist.Ingredient(
            code=code, label='_'+code, amount='2', unit='g')
        return ingredient

    def setup_ingredients(self, *codes):
        ingredients = collections.OrderedDict()
        for code in codes:
            ingredients[code] = self.get_ingredient(code)
        return ingredients
