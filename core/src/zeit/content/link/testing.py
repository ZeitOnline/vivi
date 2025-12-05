import importlib.resources

import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.author.testing
import zeit.push.testing


class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        self.config = zeit.content.article.testing.CONFIG_LAYER.config
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')

HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'source-blogs': f'file://{HERE}/blog_source.xml',
    },
    bases=(
        zeit.push.testing.CONFIG_LAYER,
        zeit.content.author.testing.CONFIG_LAYER,
        ARTICLE_CONFIG_LAYER,
    ),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, zeit.push.testing.create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER
