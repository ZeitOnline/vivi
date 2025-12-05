import importlib.resources
import re

import zope.component
import zope.testing.renormalizing

import zeit.cms.tagging.interfaces
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.cms.testing.doctest
import zeit.content.author.testing
import zeit.content.gallery.testing
import zeit.content.volume.testing
import zeit.push.testing
import zeit.wochenmarkt.testing


checker = zope.testing.renormalizing.RENormalizing(
    [(re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<GUID>')]
)
checker.transformers[0:0] = zeit.cms.testing.doctest.checker.transformers


def create_fixture(repository):
    zeit.push.testing.create_fixture(repository)
    repository['article'] = create_article()
    repository['image'] = zeit.content.image.testing.create_image()


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'zeit-comments-api-url': 'https://comments.staging.zeit.de',
        'book-recension-categories': f'file://{HERE}/tests/recension_categories.xml',
        'followings': f'file://{HERE}/tests/followings.xml',
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
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)


class FunctionalTestCase(
    zeit.cms.testing.FunctionalTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    layer = ZOPE_LAYER

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


WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    zeit.cms.testing.WSGILayer(
        zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer, create_fixture)
    )
)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


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
