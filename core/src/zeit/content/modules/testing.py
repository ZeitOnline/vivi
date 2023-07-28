import collections
import importlib.resources
import zeit.cmp.testing
import zeit.cms.content.add
import zeit.cms.testing
import zeit.content.modules
import zeit.content.text.text
import zeit.wochenmarkt.ingredients
import zeit.wochenmarkt.testing


product_config = """\
<product-config zeit.content.modules>
  jobticker-source file://{here}/tests/fixtures/jobticker.xml
  subject-source file://{here}/tests/fixtures/mail-subjects.xml
  embed-provider-source file://{here}/tests/fixtures/embed-providers.xml
  newsletter-source file://{here}/tests/fixtures/newsletter.xml
  recipe-metadata-source file://{here}/tests/fixtures/recipe-metadata.xml
  podigee-providers-source file://{here}/tests/fixtures/podigee-providers.xml
</product-config>
""".format(here=importlib.resources.files(__package__))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.cmp.testing.CONFIG_LAYER,
    zeit.wochenmarkt.testing.CONFIG_LAYER))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.ZeitCmsBrowserTestCase):

    layer = WSGI_LAYER


class IngredientsHelper:
    """Mixin for tests which need some ingredients infrastrucutre."""

    def get_ingredient(self, code, **kwargs):
        amount = kwargs.get('amount', '2')
        unit = kwargs.get('unit', 'g')
        details = kwargs.get('details', 'sautiert')
        ingredient = zeit.content.modules.recipelist.Ingredient(
            code=code, label='_' + code, amount=amount,
            unit=unit, details=details)
        return ingredient

    def setup_ingredients(self, *codes):
        ingredients = collections.OrderedDict()
        for code in codes:
            ingredients[code] = self.get_ingredient(code)
        return ingredients
