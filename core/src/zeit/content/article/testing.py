from unittest import mock
import importlib.resources
import re

import zope.component
import zope.testing.renormalizing

import zeit.cms.tagging.interfaces
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.author.testing
import zeit.content.gallery.testing
import zeit.content.volume.testing
import zeit.push.testing
import zeit.retresco.testhelper
import zeit.wochenmarkt.testing


checker = zope.testing.renormalizing.RENormalizing(
    [(re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<GUID>')]
)
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'zeit-comments-api-url': 'https://comments.staging.zeit.de',
        'book-recension-categories': f'file://{HERE}/tests/recension_categories.xml',
        'genre-url': f'file://{HERE}/tests/article-genres.xml',
        'image-display-mode-source': f'file://{HERE}/edit/tests/image-display-modes.xml',
        'legacy-display-mode-source': f'file://{HERE}/edit/tests/legacy-display-modes.xml',
        'image-variant-name-source': f'file://{HERE}/edit/tests/image-variant-names.xml',
        'legacy-variant-name-source': f'file://{HERE}/edit/tests/legacy-variant-names.xml',
        'video-layout-source': f'file://{HERE}/edit/tests/video-layouts.xml',
        'infobox-layout-source': f'file://{HERE}/edit/tests/infobox-layouts.xml',
        'template-source': f'file://{HERE}/edit/tests/templates.xml',
        'module-source': f'file://{HERE}/edit/tests/modules.xml',
        'header-module-source': f'file://{HERE}/edit/tests/header-modules.xml',
        'topicbox-teaser-amount': '5',
        'citation-layout-source': f'file://{HERE}/edit/tests/citation-layouts.xml',
        'box-layout-source': f'file://{HERE}/edit/tests/box-layouts.xml',
        'puzzleforms-source': f'file://{HERE}/edit/tests/puzzleforms.xml',
        'topicpage-filter-source': f'file://{HERE}/tests/topicpage-esqueries.json',
        'bluesky-api-timeout': 10,
    },
    bases=(
        zeit.content.author.testing.CONFIG_LAYER,
        zeit.content.gallery.testing.CONFIG_LAYER,
        zeit.content.volume.testing.CONFIG_LAYER,
        zeit.wochenmarkt.testing.CONFIG_LAYER,
    ),
    # XXX Kludge because we depend on zeit.workflow.publish_3rdparty in our tests
    patches={'zeit.workflow': {}},
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(bases=(ZOPE_LAYER,))


# This is a copy from z.c.cp ElasticsearchMockLayer with an
# additional TMS mock.
# A better solution would be a abstraction of these test mock layers
# in zeit.cms so they could be used by z.c.article and z.c.cp
class ElasticsearchMockLayer(zeit.cms.testing.Layer):
    def testSetUp(self):
        self['elasticsearch'] = mock.Mock()
        self['elasticsearch'].search.return_value = zeit.cms.interfaces.Result()
        zope.interface.alsoProvides(self['elasticsearch'], zeit.retresco.interfaces.IElasticsearch)
        zope.component.getSiteManager().registerUtility(self['elasticsearch'])
        self['tms'] = mock.Mock()
        self['tms'].get_topicpage_documents.return_value = zeit.cms.interfaces.Result()
        self['tms'].get_related_documents.return_value = zeit.cms.interfaces.Result()

        zope.interface.alsoProvides(self['tms'], zeit.retresco.interfaces.ITMS)
        zope.component.getSiteManager().registerUtility(self['tms'])

    def testTearDown(self):
        zope.component.getSiteManager().unregisterUtility(self['elasticsearch'])
        del self['elasticsearch']
        zope.component.getSiteManager().unregisterUtility(self['tms'])
        del self['tms']


ELASTICSEARCH_MOCK_LAYER = ElasticsearchMockLayer()


class ArticleLayer(zeit.cms.testing.Layer):
    defaultBases = (PUSH_LAYER,)

    def testSetUp(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        prop = connector._get_properties('http://xml.zeit.de/online/2007/01/Somalia')
        prop[zeit.cms.tagging.testing.KEYWORD_PROPERTY] = 'Testtag|Testtag2|Testtag3'


LAYER = ArticleLayer()
MOCK_LAYER = zeit.cms.testing.Layer(
    name='MockLayer',
    bases=(
        ZOPE_LAYER,
        zeit.retresco.testhelper.ELASTICSEARCH_MOCK_LAYER,
        zeit.retresco.testhelper.TMS_MOCK_LAYER,
    ),
)


class FunctionalTestCase(
    zeit.cms.testing.FunctionalTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    layer = LAYER

    def get_article(self):
        wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
        article = create_article()
        article.keywords = [wl.get(tag) for tag in wl.tags]
        return article

    def get_factory(self, article, factory_name):
        import zope.component

        import zeit.content.article.edit.body
        import zeit.edit.interfaces

        body = zeit.content.article.edit.body.EditableBody(article, article.xml.find('body'))
        return zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, factory_name)


def create_article():
    from zeit.content.article.article import Article
    from zeit.content.article.interfaces import IArticle
    import zeit.cms.content.field

    article = Article()
    zeit.cms.content.field.apply_default_values(article, IArticle)
    article.year = 2011
    article.title = 'title'
    article.ressort = 'Deutschland'
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
    return article


WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(bases=(WSGI_LAYER,))
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(bases=(HTTP_LAYER,))


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER

    WIDGET_SELECTOR = 'xpath=//label[@for="%s"]/../../*[@class="widget"]'

    def assert_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.assertText(path, text)

    def wait_for_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.waitForText(path, text)
