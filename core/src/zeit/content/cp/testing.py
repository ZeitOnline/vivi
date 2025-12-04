from unittest import mock
import importlib.resources
import re

from sqlalchemy.dialects import postgresql
import pendulum
import transaction
import zope.component
import zope.interface
import zope.security.management
import zope.testing.renormalizing

from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
import zeit.cms.content.field
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.testing.doctest
import zeit.cms.workflow.interfaces
import zeit.content.image.testing
import zeit.content.modules.testing
import zeit.content.text.testing
import zeit.retresco.interfaces
import zeit.retresco.testhelper


def create_fixture(repository):
    article = Article()
    zeit.cms.content.field.apply_default_values(article, IArticle)
    article.year = 2025
    article.title = 'Cookie monster'
    article.ressort = 'Politik'
    info = zeit.cms.workflow.interfaces.IPublishInfo(article)
    info.published = True
    info.date_last_published_semantic = pendulum.datetime(2025, 11, 10)
    repository['article'] = article

    content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
    content.title = 'foo'
    repository['folder'] = zeit.cms.repository.folder.Folder()
    repository['folder']['testcontent'] = content

    repository['imagefolder'] = zeit.cms.repository.folder.Folder()
    repository['imagefolder']['image'] = zeit.content.image.testing.create_image()
    repository['imagegroup'] = zeit.content.image.testing.create_image_group()


FIXTURES = importlib.resources.files(__package__) / 'tests/fixtures'
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'block-layout-source': f'file://{FIXTURES}/layout.xml',
        'region-config-source': f'file://{FIXTURES}/regions.xml',
        'area-config-source': f'file://{FIXTURES}/areas.xml',
        'module-config-source': f'file://{FIXTURES}/blocks.xml',
        'cp-extra-url': f'file://{FIXTURES}/cpextra.xml',
        'cp-types-url': f'file://{FIXTURES}/cp-types.xml',
        'topicpage-filter-source': f'file://{FIXTURES}/filter.json',
        'layout-image-path': '/data/cp-layouts',
        'layout-css-path': '/data/cp-layouts/layouts.css',
        'header-image-variant': 'cinema',
        'cp-automatic-feed-source': f'file://{FIXTURES}/feeds.xml',
        'area-color-themes-source': f'file://{FIXTURES}/area-color-themes.xml',
        'reach-service-source': f'file://{FIXTURES}/reach-services.xml',
        'sql-query-add-clauses': 'published=true',
    },
    patches={
        'zeit.edit': {
            'rules-url': 'file://%s/tests/fixtures/example_rules.py'
            % importlib.resources.files(__package__)
        },
        'zeit.retresco': {'topicpage-prefix': '/folder'},
    },
    bases=(
        zeit.content.image.testing.CONFIG_LAYER,
        zeit.content.modules.testing.CONFIG_LAYER,
        zeit.content.text.testing.CONFIG_LAYER,
    ),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)


class CPTemplateLayer(zeit.cms.testing.Layer):
    # BBB We have too many tests that use lead/informatives. Rewriting them
    # to create their own areas is too time-consuming to do at once.

    def setUp(self):
        self['cp-template-patch'] = mock.patch(
            'zeit.content.cp.centerpage.CenterPage.default_template',
            new=(
                importlib.resources.files(__package__) / 'tests/fixtures/cp-template.xml'
            ).read_text('utf-8'),
        )
        self['cp-template-patch'].start()

    def tearDown(self):
        self['cp-template-patch'].stop()
        del self['cp-template-patch']


CP_TEMPLATE_LAYER = CPTemplateLayer(ZOPE_LAYER)


LAYER = zeit.cms.testing.Layer(
    (CP_TEMPLATE_LAYER, zeit.retresco.testhelper.ELASTICSEARCH_MOCK_LAYER)
)


checker = zope.testing.renormalizing.RENormalizing(
    [
        (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<GUID>'),
        (re.compile('[0-9a-f]{32}'), '<MD5>'),
        (
            re.compile(
                '[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}'
                r'(\.[0-9]+)?(\+[0-9]{2}:[0-9]{2})?'
            ),
            '<ISO DATE>',
        ),
        (
            re.compile(
                '[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} '
                '[0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4}'
            ),
            '<RFC822 DATE>',
        ),
    ]
)

checker.transformers[0:0] = zeit.cms.testing.doctest.checker.transformers


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('checker', checker)
    kw.setdefault('layer', LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER

    def compile_sql(self, stmt):
        return str(
            stmt.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})
        )

    def create_content(self, name, title):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        content.teaserTitle = title
        self.repository[name] = content
        transaction.commit()
        return content

    def create_and_checkout_centerpage(self, name='cp', contents=None):
        transaction.abort()
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        repository[name] = zeit.content.cp.centerpage.CenterPage()
        cp = zeit.cms.checkout.interfaces.ICheckoutManager(repository[name]).checkout()
        if contents:
            for content in contents:
                cp.body['lead'].create_item('teaser').append(content)
        transaction.commit()
        return cp


WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)
WSGI_SQL_LAYER = zeit.cms.testing.WSGILayer(
    bases=(
        CPTemplateLayer(),
        zeit.retresco.testhelper.ELASTICSEARCH_MOCK_LAYER,
        zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer),
    )
)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_SQL_LAYER)
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(FunctionalTestCase, zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
    skin = 'vivi'

    window_width = 1600
    window_height = 1000

    def setUp(self):
        super().setUp()

    def get_module(self, area, text):
        return (
            'xpath=//div'
            '[@class="module represents-content-object %s-module"]'
            '[contains(string(.), "%s")]' % (area, text)
        )

    def open_centerpage(self, create_cp=True):
        if create_cp:
            self.create_and_checkout_centerpage()
        s = self.selenium
        self.open('/workingcopy/zope.user/cp/@@edit.html')
        s.waitForElementPresent('css=div.landing-zone')

    def create_clip(self):
        # Creat clip
        s = self.selenium
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('//li[@uniqueid="Clip"]')
        # Open clip
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def clip_object(self, match):
        s = self.selenium
        s.click('xpath=//td[contains(string(.), "%s")]' % match)
        s.waitForElementPresent('css=div#bottomcontent > div')
        s.dragAndDropToObject(
            'xpath=//td[contains(string(.), "%s")]' % match, '//li[@uniqueid="Clip"]'
        )
        s.pause(500)

    def create_teaserlist(self):
        self.open_centerpage()
        self.create_block('teaser', 'informatives')

    def create_block(self, block_type, area_id):
        s = self.selenium
        s.click('link=Struktur')
        library_module = 'css=.module[cms\\:block_type=%s]' % block_type
        s.waitForElementPresent(library_module)
        s.dragAndDropToObject(
            library_module, 'css=#%s .landing-zone.action-cp-module-droppable' % area_id, '10,10'
        )
        s.waitForElementPresent('css=div.type-%s' % block_type)

    def create_content_and_fill_clipboard(self):
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        interaction = zope.security.management.getInteraction()
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            interaction.participations[0].principal
        )
        clipboard.addClip('Clip')
        clip = clipboard['Clip']
        for i in range(1, 4):
            content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
            content.teaserTitle = content.title = 'c%s teaser' % i
            name = 'c%s' % i
            repository[name] = content
            clipboard.addContent(clip, repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        self.open('/')
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')
