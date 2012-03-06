# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import SimpleHTTPServer
import __future__
import gocept.selenium.ztk
import os
import pkg_resources
import re
import transaction
import zeit.cms.testing
import zeit.workflow.testing
import zope.testing.doctest
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.cp>
    block-layout-source file://%s
    cp-extra-url file://%s
    cp-feed-max-items 200
    cp-types-url file://%s
    feed-update-minimum-age 30
    rss-folder rss
    rules-url file://%s
    scales-fullgraphical-url file://%s
</product-config>
""" % (pkg_resources.resource_filename(__name__, 'layout.xml'),
    pkg_resources.resource_filename(__name__, 'cpextra.xml'),
    pkg_resources.resource_filename(__name__, 'cp-types.xml'),
    pkg_resources.resource_filename('zeit.content.cp.tests.fixtures',
                                    'example_rules.py'),
    pkg_resources.resource_filename(__name__, 'scales-fullgraphical.xml'),
       )


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config +
    zeit.workflow.testing.product_config)


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler,
                     SimpleHTTPServer.SimpleHTTPRequestHandler):

    serve_from = pkg_resources.resource_filename(__name__, 'tests/feeds/')
    serve_favicon = False

    def send_head(self):
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


HTTPLayer, httpd_port = zeit.cms.testing.HTTPServerLayer(RequestHandler)


class FeedServer(HTTPLayer, layer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass



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


selenium_layer = gocept.selenium.ztk.Layer(layer)


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = selenium_layer
    skin = 'vivi'

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        # We need a certain min width/height which is given on larger screens.
        # For smaller screens the default window is too small. Maximizing the
        # test window is large enough.
        self.selenium.windowMaximize()

    def get_module(self, area, text):
        return ('xpath=//div[@class="module %s-module"]'
                '[contains(string(.), "%s")]' % (area, text))

    def open_centerpage(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                repository = zope.component.getUtility(
                    zeit.cms.repository.interfaces.IRepository)
                repository['cp'] = zeit.content.cp.centerpage.CenterPage()
                cp = zeit.cms.checkout.interfaces.ICheckoutManager(
                    repository['cp']).checkout()
        transaction.commit()

        s = self.selenium
        self.open('/workingcopy/zope.user/cp/@@edit.html')
        s.waitForElementPresent('css=div.landing-zone')

    def create_clip(self):
        # Creat clip
        s = self.selenium
        s.click('id=clip-add-folder-link')
        s.type('id=clip-add-folder-title', 'Clip')
        s.click('id=clip-add-folder-submit')
        s.waitForElementPresent('link=Clip')
        # Open clip
        s.click('//li[@uniqueid="Clip"]')
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
        s = self.selenium
        s.click('link=*Add block*')
        teaser_module = self.get_module('informatives', 'List of teasers')
        s.waitForElementPresent(teaser_module)
        s.dragAndDropToObject(
            teaser_module,
            'css=.landing-zone.action-informatives-module-droppable')
        s.waitForElementPresent('css=div.type-teaser')

    def create_content_and_fill_clipboard(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                repository = zope.component.getUtility(
                    zeit.cms.repository.interfaces.IRepository)
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
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
        s.click('//li[@uniqueid="Clip"]')
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
