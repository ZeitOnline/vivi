# coding: utf-8
import gocept.selenium
import pkg_resources
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.content.image.testing


product_config = """
<product-config zeit.content.volume>
    volume-cover-source file://{here}/tests/fixtures/volume-covers.xml
    default-teaser-text Teäser {{name}}/{{year}}
    access-control-config file://{here}/tests/fixtures/access-control.xml
    access-control-webtrekk-url https://webtrekkapi.foo
    access-control-webtrekk-timeout 10
    access-control-webtrekk-username foo
    access-control-webtrekk-password bar
    access-control-webtrekk-customerId 123
</product-config>
""".format(here=pkg_resources.resource_filename(__name__, '.'))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.content.cp.testing.CONFIG_LAYER,
    zeit.content.image.testing.CONFIG_LAYER))


# XXX copy&paste from zeit.push.testing
class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):

    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing
        config = zeit.content.article.testing.product_config
        self.config = self.loadConfiguration(config, self.package)
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(
    CONFIG_LAYER, ARTICLE_CONFIG_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(CELERY_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
