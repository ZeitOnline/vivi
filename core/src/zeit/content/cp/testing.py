from unittest import mock
import gocept.selenium
import importlib.resources
import plone.testing
import re
import transaction
import zeit.cms.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.modules.testing
import zeit.content.text.testing
import zeit.retresco.interfaces
import zeit.retresco.testhelper
import zope.component
import zope.interface
import zope.security.management
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.cp>
    block-layout-source file://{fixtures}/layout.xml
    region-config-source file://{fixtures}/regions.xml
    area-config-source file://{fixtures}/areas.xml
    module-config-source file://{fixtures}/blocks.xml
    cp-extra-url file://{fixtures}/cpextra.xml
    cp-types-url file://{fixtures}/cp-types.xml
    topicpage-filter-source file://{fixtures}/filter.json
    layout-image-path /data/cp-layouts
    layout-css-path /data/cp-layouts/layouts.css
    header-image-variant cinema
    cp-automatic-feed-source file://{fixtures}/feeds.xml
    area-color-themes-source file://{fixtures}/area-color-themes.xml
    reach-service-source file://{fixtures}/reach-services.xml
</product-config>
""".format(
    fixtures='%s/tests/fixtures' % importlib.resources.files(__package__))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    patches={'zeit.edit': {
        'rules-url': 'file://%s/tests/fixtures/example_rules.py' %
        importlib.resources.files(__package__)},
        'zeit.retresco': {'topicpage-prefix': '/2007'},
    }, bases=(
        zeit.content.image.testing.CONFIG_LAYER,
        zeit.content.modules.testing.CONFIG_LAYER,
        zeit.content.text.testing.CONFIG_LAYER))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class CPTemplateLayer(plone.testing.Layer):
    # BBB We have too many tests that use lead/informatives. Rewriting them
    # to create their own areas is too time-consuming to do at once.

    defaultBases = (ZOPE_LAYER,)

    def setUp(self):
        self['cp-template-patch'] = mock.patch(
            'zeit.content.cp.centerpage.CenterPage.default_template',
            new=(importlib.resources.files(__package__) /
                 'tests/fixtures/cp-template.xml').read_text('utf-8'))
        self['cp-template-patch'].start()

    def tearDown(self):
        self['cp-template-patch'].stop()
        del self['cp-template-patch']


CP_TEMPLATE_LAYER = CPTemplateLayer()


LAYER = plone.testing.Layer(name='Layer', bases=(
    CP_TEMPLATE_LAYER, zeit.retresco.testhelper.ELASTICSEARCH_MOCK_LAYER))


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
        '<GUID>'),
    (re.compile('[0-9a-f]{32}'), '<MD5>'),
    (re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}'
                r'(\.[0-9]+)?(\+[0-9]{2}:[0-9]{2})?'), '<ISO DATE>'),
    (re.compile('[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} '
                '[0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4}'), '<RFC822 DATE>'),
])

checker.transformers[0:0] = zeit.cms.testing.checker.transformers


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('checker', checker)
    kw.setdefault('layer', LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER

    def create_content(self, name, title):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        content.teaserTitle = title
        self.repository[name] = content
        return content

    def create_and_checkout_centerpage(self, name='cp', contents=None):
        transaction.abort()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository[name] = zeit.content.cp.centerpage.CenterPage()
        cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            repository[name]).checkout()
        if contents:
            for content in contents:
                cp['lead'].create_item('teaser').append(content)
        transaction.commit()
        return cp

    def create_lead_teaser(self, order=None):
        lead = self.repository['cp']['lead']
        lead.automatic = True
        lead.automatic_type = 'custom'
        lead.count = 1
        lead.query = (('channels', 'eq', 'International', 'Nahost'),)
        if order:
            lead.query_order = order
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        return lead


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


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
        return ('xpath=//div'
                '[@class="module represents-content-object %s-module"]'
                '[contains(string(.), "%s")]' % (area, text))

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
            'xpath=//td[contains(string(.), "%s")]' % match,
            '//li[@uniqueid="Clip"]')
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
            library_module,
            'css=#%s .landing-zone.action-cp-module-droppable' % area_id,
            '10,10')
        s.waitForElementPresent('css=div.type-%s' % block_type)

    def create_content_and_fill_clipboard(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        interaction = zope.security.management.getInteraction()
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            interaction.participations[0].principal)
        clipboard.addClip('Clip')
        clip = clipboard['Clip']
        for i in range(1, 4):
            content = (zeit.cms.testcontenttype.testcontenttype.
                       ExampleContentType())
            content.teaserTitle = content.title = (
                'c%s teaser' % i)
            name = 'c%s' % i
            repository[name] = content
            clipboard.addContent(
                clip, repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        self.open('/')
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')
