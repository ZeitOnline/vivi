import SimpleHTTPServer
import __future__
import gocept.httpserverlayer.custom
import gocept.httpserverlayer.wsgi
import gocept.selenium
import os
import pkg_resources
import re
import time
import transaction
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.workflow.testing
import zope.testing.doctest
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.cp>
    block-layout-source file://%s
    area-kind-source file://%s
    area-config-source file://%s
    region-config-source file://%s
    bar-layout-source file://%s
    cp-extra-url file://%s
    cp-feed-max-items 200
    cp-types-url file://%s
    feed-update-minimum-age 30
    rss-folder rss
    scales-fullgraphical-url file://%s
    layout-image-path /data/cp-layouts
</product-config>

<product-config zeit.edit>
    rules-url file://%s
</product-config>
""" % (
    pkg_resources.resource_filename(__name__, 'layout.xml'),
    pkg_resources.resource_filename(__name__, 'area-kinds.xml'),
    pkg_resources.resource_filename(__name__, 'areas.xml'),
    pkg_resources.resource_filename(__name__, 'regions.xml'),
    pkg_resources.resource_filename(__name__, 'bar-layout.xml'),
    pkg_resources.resource_filename(__name__, 'cpextra.xml'),
    pkg_resources.resource_filename(__name__, 'cp-types.xml'),
    pkg_resources.resource_filename(__name__, 'scales-fullgraphical.xml'),
    pkg_resources.resource_filename(
        'zeit.content.cp.tests.fixtures', 'example_rules.py'),
)


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config +
    zeit.workflow.testing.product_config)


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler,
                     SimpleHTTPServer.SimpleHTTPRequestHandler):

    serve_from = pkg_resources.resource_filename(__name__, 'tests/feeds/')
    serve_favicon = False
    delay_request_by = 0

    def send_head(self):
        time.sleep(self.delay_request_by)
        if self.path == '/favicon.ico' and not self.serve_favicon:
            self.path = '/does-not-exist'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    def translate_path(self, path):
        cur_path = os.getcwd()
        os.chdir(self.serve_from)
        try:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
                self, path)
        finally:
            os.chdir(cur_path)

    def guess_type(self, path):
        return 'application/xml'


FEED_SERVER_LAYER = gocept.httpserverlayer.custom.Layer(
    RequestHandler, name='FeedServerLayer', module=__name__, bases=(layer,))


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),
    (re.compile('[0-9a-f]{32}'), "<MD5>"),
    (re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(\+[0-9]{2}:[0-9]{2})?'),
     "<ISO DATE>"),
    (re.compile('[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4}'),
     "<RFC822 DATE>"),
])

checker.transformers[0:0] = zeit.cms.testing.checker.transformers


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('checker', checker)
    kw.setdefault('layer', layer)
    kw.setdefault('globs', dict(with_statement=__future__.with_statement))
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = layer

    def create_content(self, name, title):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        content.teaserTitle = title
        self.repository[name] = content
        return content

    def create_and_checkout_centerpage(self, name='cp', contents=[]):
        transaction.abort()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository[name] = zeit.content.cp.centerpage.CenterPage()
        cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            repository[name]).checkout()
        for content in contents:
            cp['lead'].create_item('teaser').append(content)
        transaction.commit()
        return cp


WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(layer,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class SeleniumTestCase(FunctionalTestCase, zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
    skin = 'vivi'

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        # We need a certain min width/height which is given on larger screens.
        # For smaller screens the default window is too small. Maximizing the
        # test window is large enough.
        self.selenium.windowMaximize()

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
                       TestContentType())
            content.teaserTitle = content.shortTeaserTitle = (
                u'c%s teaser' % i)
            name = 'c%s' % i
            repository[name] = content
            clipboard.addContent(
                clip, repository[name], name, insert=True)
        quiz = zeit.content.quiz.quiz.Quiz()
        quiz.teaserTitle = quiz.shortTeaserTitle = u'MyQuiz'
        repository['my_quiz'] = quiz
        transaction.commit()

        s = self.selenium
        self.open('/')
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def create_filled_teaserlist(self):
        s = self.selenium
        self.create_content_and_fill_clipboard()
        self.create_teaserlist()
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c3 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c2 teaser')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]',
            'css=div.type-teaser')
        s.waitForTextPresent('c1 teaser')
