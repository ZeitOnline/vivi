import importlib.resources

# API re-imports
# ruff: noqa: F401
from .browser import Browser, BrowserAssertions, BrowserTestCase
from .celery import CeleryWorkerLayer, wait_for_celery
from .doctest import FunctionalDocFileSuite, optionflags
from .http import HTTPLayer, WSGIServerLayer
from .layer import Layer
from .mock import ResetMocks
from .pytest import copy_inherited_functions
from .selenium import SeleniumTestCase, WebdriverLayer
from .utils import xmltotext
from .zope import (
    AdditionalZCMLLayer,
    FunctionalTestCase,
    ProductConfigLayer,
    WSGILayer,
    ZCMLLayer,
    ZopeLayer,
    create_interaction,
    interaction,
    set_site,
    site,
)


HERE = importlib.resources.files('zeit.cms')
CONFIG_LAYER = ProductConfigLayer(
    {
        'environment': 'testing',
        'tracing-instrument': 'True',
        'source-serie': f'file://{HERE}/content/serie.xml',
        'source-ressorts': f'file://{HERE}/content/ressorts.xml',
        'source-keyword': f'file://{HERE}/content/zeit-ontologie-prism.xml',
        'source-products': f'file://{HERE}/content/products.xml',
        'source-badges': f'file://{HERE}/asset/badges.xml',
        'source-channels': f'file://{HERE}/content/ressorts.xml',
        'source-printressorts': f'file://{HERE}/content/print-ressorts.xml',
        'source-manual': f'file://{HERE}/content/manual.xml',
        'config-retractlog': f'file://{HERE}/retractlog/retractlog.xml',
        'checkout-lock-timeout': '3600',
        'checkout-lock-timeout-temporary': '30',
        'preview-prefix': 'http://localhost/preview-prefix/',
        'live-prefix': 'http://localhost/live-prefix/',
        'image-live-prefix': 'http://localhost/img-live-prefix/',
        'friebert-wc-preview-prefix': '/wcpreview',
        'breadcrumbs-use-common-metadata': 'true',
        'cache-regions': 'config, feature, short_term',
        'cache-expiration-config': '600',
        'cache-expiration-feature': '15',
        'cache-expiration-short_term': '120',
        'feature-toggle-source': f'file://{HERE}/content/feature-toggle.xml',
        'sso-cookie-name-prefix': 'my_sso_',
        'sso-cookie-domain': '',
        'sso-expiration': '300',
        'sso-algorithm': 'RS256',
        'sso-private-key-file': f'{HERE}/tests/sso-private.pem',
        'source-api-mapping': 'product=zeit.cms.content.sources.ProductSource',
        # We just need a dummy XML file
        'checkin-webhook-config': f'file://{HERE}/content/ressorts.xml',
        'checkin-revisions-config': f'file://{HERE}/content/checkin-revisions.xml',
    },
    patches={
        'zeit.connector': {
            'repository-path': str((importlib.resources.files('zeit.connector') / 'testcontent'))
        }
    },
)
ZCML_LAYER = ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
ZOPE_LAYER = ZopeLayer(ZCML_LAYER)
WSGI_LAYER = WSGILayer(ZOPE_LAYER)
HTTP_LAYER = WSGIServerLayer(WSGI_LAYER)
WEBDRIVER_LAYER = WebdriverLayer(HTTP_LAYER)


# These ugly names are due to two reasons:
# 1. zeit.cms.testing contains both general test mechanics *and*
#    specific test infrastructure/layers for zeit.cms itself
# 2. pytest does not allow for subclassing a TestCase and changing its layer
#    (for the same reason as copy_inherited_functions above).


class ZeitCmsTestCase(FunctionalTestCase):
    layer = ZOPE_LAYER


class ZeitCmsBrowserTestCase(BrowserTestCase):
    layer = WSGI_LAYER
