import importlib.resources

import zeit.cms.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'recipe-genres': 'rezept,rezept-vorstellung',
        'categories-url': f'file://{HERE}/tests/fixtures/categories.xml',
        'ingredients-url': f'file://{HERE}/tests/fixtures/ingredients.xml',
    },
    bases=(zeit.cms.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER
