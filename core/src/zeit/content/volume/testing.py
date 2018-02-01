# coding: utf-8
import gocept.httpserverlayer.wsgi
import gocept.selenium
import pkg_resources
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.content.image.testing
import zeit.workflow.testing


product_config = """
<product-config zeit.content.volume>
    volume-cover-source file://{here}/tests/fixtures/volume-covers.xml
    dav-archive-url test
    toc-product-ids ZEI BAD
    toc-num-empty-columns 3
    default-teaser-text Teäser {{name}}/{{year}}
</product-config>
""".format(here=pkg_resources.resource_filename(__name__, '.'))

# Prevent circular dependency
article_config = """
<product-config zeit.content.article>
    image-display-mode-source file://{article}/image-display-modes.xml
    legacy-display-mode-source file://{article}/legacy-display-modes.xml
    image-variant-name-source file://{article}/image-variant-names.xml
    legacy-variant-name-source file://{article}/legacy-variant-names.xml
</product-config>
""".format(article=pkg_resources.resource_filename(
    'zeit.content.article.edit.tests', ''))

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=(
        product_config +
        article_config +
        zeit.cms.testing.cms_product_config +
        zeit.content.image.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.workflow.testing.product_config
    ))
# XXX We need a separate celery layer per ZCML: While CeleryWorkerLayer only
# needs the ZODB, this is combined with ZCML in FunctionalTestSetup -- which
# we should get rid of.
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(
    name='CeleryLayer', bases=(ZCML_LAYER,))


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(CELERY_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER
