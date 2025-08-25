# coding: utf-8
import importlib.resources

from pendulum import datetime

from zeit.cms.repository.folder import Folder
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.volume.volume import Volume
import zeit.cms.content.sources
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.content.image.testing
import zeit.push.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'volume-cover-source': f'file://{HERE}/tests/fixtures/volume-covers.xml',
        'default-teaser-text': 'Teäser {name}/{year}',
        'access-control-config': f'file://{HERE}/tests/fixtures/access-control.xml',
        'access-control-webtrekk-url': 'https://webtrekkapi.foo',
        'access-control-webtrekk-timeout': '10',
        'access-control-webtrekk-username': 'foo',
        'access-control-webtrekk-password': 'bar',
        'access-control-webtrekk-customerid': '123',
    },
    bases=(zeit.content.cp.testing.CONFIG_LAYER, zeit.push.testing.CONFIG_LAYER),
)


# XXX copy&paste from zeit.push.testing
class ArticleConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing

        self.config = zeit.content.article.testing.CONFIG_LAYER.config
        super().setUp()


ARTICLE_CONFIG_LAYER = ArticleConfigLayer({}, package='zeit.content.article')
ZCML_LAYER = zeit.cms.testing.ZCMLLayer((CONFIG_LAYER, ARTICLE_CONFIG_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
BROWSER_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


WORKFLOW_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='ftesting-workflow.zcml', bases=(CONFIG_LAYER, ARTICLE_CONFIG_LAYER)
)
WORKFLOW_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(WORKFLOW_LAYER)
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(WORKFLOW_ZOPE_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(CELERY_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_LAYER)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)

SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='ftesting-workflow.zcml',
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, ARTICLE_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(SQL_ZCML_LAYER)
SQL_WSGI_LAYER = zeit.cms.testing.WSGILayer(SQL_ZOPE_LAYER, name='SQLWSGILayer')


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = BROWSER_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER


class SQLTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = SQL_ZOPE_LAYER

    def create_volume(self, year, name, product='ZEI', published=True):
        volume = Volume()
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product(product)
        if published:
            volume.date_digital_published = datetime(year, name, 1)
            info = IPublishInfo(volume)
            info.published = True
            info.date_first_released = datetime(2025, 1, 1)
        year = str(year)
        name = '%02d' % name
        self.repository[year] = Folder()
        self.repository[year][name] = Folder()
        self.repository[year][name]['ausgabe'] = volume
        return self.repository[year][name]['ausgabe']
