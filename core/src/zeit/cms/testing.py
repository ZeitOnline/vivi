# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import BaseHTTPServer
import __future__
import contextlib
import copy
import gocept.selenium.ztk
import inspect
import logging
import pkg_resources
import random
import re
import string
import sys
import threading
import time
import transaction
import urllib2
import xml.sax.saxutils
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.component
import zope.publisher.browser
import zope.security.management
import zope.security.testing
import zope.site.hooks
import zope.testing.renormalizing


def ZCMLLayer(
    config_file, module=None, name=None, allow_teardown=True,
    product_config=None):
    if module is None:
        module = stack = inspect.stack()[1][0].f_globals['__name__']
    if name is None:
        name = 'ZCMLLayer(%s)' % config_file
    if not config_file.startswith('/'):
        config_file = pkg_resources.resource_filename(module, config_file)
    if product_config is True:
        product_config = cms_product_config
    def setUp(cls):
        cls.setup = zope.app.testing.functional.FunctionalTestSetup(
            config_file, product_config=product_config)

    def tearDown(cls):
        cls.setup.tearDownCompletely()
        if not allow_teardown:
            raise NotImplementedError

    layer = type(name, (object,), dict(
        __module__=module,
        setUp=classmethod(setUp),
        tearDown=classmethod(tearDown),
    ))
    return layer


class HTTPServer(BaseHTTPServer.HTTPServer):

    def __init__(self, *args):
        BaseHTTPServer.HTTPServer.__init__(self, *args)
        self.errors = []

    def handle_error(self, request, client_address):
        self.errors.append((request, client_address))


def HTTPServerLayer(request_handler):
    """Factory for a layer which opens a HTTP port."""
    module = stack = inspect.stack()[1][0].f_globals['__name__']
    port = random.randint(30000, 40000)

    def setUp(cls):
        cls.httpd_running = True
        def run():
            server_address = ('localhost', port)
            cls.httpd = HTTPServer(server_address, request_handler)
            while cls.httpd_running:
                cls.httpd.handle_request()
        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
        # XXX this is a little kludgy
        time.sleep(0.001)

    def tearDown(cls):
        cls.httpd_running = False
        try:
            urllib2.urlopen('http://localhost:%s/die' % port, timeout=1)
        except urllib2.URLError:
            pass

    def testTearDown(cls):
        cls.httpd.errors[:] = []
        request_handler.tearDown()

    layer = type('HTTPLayer(%s)' % port, (object,), dict(
        __module__=module,
        setUp=classmethod(setUp),
        tearDown=classmethod(tearDown),
        testTearDown=classmethod(testTearDown),
    ))
    return layer, port


class BaseHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Handler for testing which does not log to STDOUT."""

    def log_message(self, format, *args):
        pass

    @classmethod
    def tearDown(cls):
        pass


cms_product_config = string.Template("""\
<product-config zeit.cms>
  source-serie file://${base}/content/serie.xml
  source-navigation file://${base}/content/navigation.xml
  source-print-ressort file://${base}/content/print-ressort.xml
  source-keyword file://${base}/content/zeit-ontologie-prism.xml
  source-products file://${base}/content/products.xml
  source-badges file://${base}/asset/badges.xml

  preview-prefix http://localhost/preview-prefix
  live-prefix http://localhost/live-prefix
  development-preview-prefix http://localhost/development-preview-prefix

  suggest-keyword-email-address none@testing
  suggest-keyword-real-name Dr. No
</product-config>
""").substitute(
    base=pkg_resources.resource_filename(__name__, ''))


cms_layer = ZCMLLayer('ftesting.zcml', product_config=True)
selenium_layer = gocept.selenium.ztk.Layer(cms_layer)


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>'),
    (re.compile('0x[0-9a-f]+'), "0x..."),
    (re.compile(r'/\+\+noop\+\+[0-9a-f]+'), ''),
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),
])


def setUpDoctests(test):
    test.old_product_config = copy.deepcopy(
        zope.app.appsetup.product.saveConfiguration())
    config = test.globs.get('product_config', {})
    __traceback_info__ = (config,)
    setup_product_config(config)


def tearDown(test):
    zope.security.management.endInteraction()
    # only for functional tests
    if hasattr(test, 'globs'):
        old_site = test.globs.get('old_site')
        if old_site is not None:
            zope.site.hooks.setSite(old_site)
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    connector._reset()
    old_config = getattr(test, 'old_product_config', None)
    if old_config is not None:
        zope.app.appsetup.product.restoreConfiguration(old_config)


def setup_product_config(product_config={}):
    zope.app.appsetup.product._configs.update(product_config)


optionflags = (doctest.REPORT_NDIFF +
               doctest.INTERPRET_FOOTNOTES +
               doctest.NORMALIZE_WHITESPACE +
               doctest.ELLIPSIS)


def DocFileSuite(*paths, **kw):
    kw['package'] = doctest._normalize_module(kw.get('package'))
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)
    return doctest.DocFileSuite(*paths, **kw)


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', cms_layer)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    kw['setUp'] = setUpDoctests
    kw['tearDown'] = tearDown
    kw.setdefault('globs', {})['product_config'] = kw.pop(
        'product_config', {})
    kw['globs']['with_statement'] = __future__.with_statement
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)

    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer

    return test


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = cms_layer
    product_config = {}

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.old_product_config = copy.deepcopy(
            zope.app.appsetup.product.saveConfiguration())
        setup_product_config(self.product_config)
        zope.site.hooks.setSite(self.getRootFolder())
        zeit.cms.testing.create_interaction(u'zope.user')

    def tearDown(self):
        zeit.cms.testing.tearDown(self)
        zope.site.hooks.setSite(None)
        super(FunctionalTestCase, self).tearDown()


class SeleniumTestCase(gocept.selenium.ztk.TestCase):

    layer = selenium_layer
    skin = 'cms'
    log_errors = False
    log_errors_ignore = ()
    level = 2

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        if self.log_errors:
            with site(self.getRootFolder()):
                error_log = zope.component.getUtility(
                    zope.error.interfaces.IErrorReportingUtility)
                error_log.copy_to_zlog = True
                error_log._ignored_exceptions = self.log_errors_ignore
            self.log_handler = logging.StreamHandler(sys.stdout)
            logging.root.addHandler(self.log_handler)
            self.old_log_level = logging.root.level
            logging.root.setLevel(logging.ERROR)
            transaction.commit()
        self.selenium.getEval('window.sessionStorage.clear()')

    def tearDown(self):
        zeit.cms.testing.tearDown(self)
        super(SeleniumTestCase, self).tearDown()
        if self.log_errors:
            logging.root.removeHandler(self.log_handler)
            logging.root.setLevel(self.old_log_level)

    def open(self, path, auth='user:userpw'):
        auth_sent = getattr(self.layer, 'auth_sent', None)
        if auth and auth != auth_sent:
            # Only set auth when it changed. Firefox will be confused
            # otherwise.
            self.layer.auth_sent = auth
            auth = auth + '@'
        else:
            auth = ''
        self.selenium.open(
            'http://%s%s/++skin++%s%s' % (
                auth, self.selenium.server, self.skin, path))

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))


def click_wo_redirect(browser, *args, **kwargs):
    browser.mech_browser.set_handle_redirect(False)
    try:
        try:
            browser.getLink(*args, **kwargs).click()
        except urllib2.HTTPError, e:
            print str(e)
            print e.hdrs.get('location')
    finally:
        browser.mech_browser.set_handle_redirect(True)


def set_site(site=None):
    """Encapsulation of the getSite/setSite-dance.

    Sets the given site, preserves the old site in the globs,
    where it will be reset by our FunctionalDocFileSuite's tearDown.
    """

    globs = sys._getframe(1).f_locals
    globs['old_site'] = zope.site.hooks.getSite()
    if site is None:
        site = globs['getRootFolder']()
    zope.site.hooks.setSite(site)


def create_interaction(name=u'zope.user'):
    principal = zope.security.testing.Principal(
        name, groups=['zope.Authenticated'])
    request = zope.publisher.browser.TestRequest()
    request.setPrincipal(principal)
    zope.security.management.newInteraction(request)
    return principal


@contextlib.contextmanager
def interaction(principal_id=u'zope.user'):
    principal = create_interaction(principal_id)
    yield principal
    zope.security.management.endInteraction()


@contextlib.contextmanager
def site(root):
    old_site = zope.site.hooks.getSite()
    zope.site.hooks.setSite(root)
    yield
    zope.site.hooks.setSite(old_site)


class BrowserAssertions(object):

    def assert_ellipsis(self, want, got=None):
        import difflib
        import doctest
        if got is None:
            got = self.browser.contents
        # normalize whitespace
        norm_want = ' '.join(want.split())
        norm_got = ' '.join(got.split())
        if doctest._ellipsis_match(norm_want, norm_got):
            return True
        # Report ndiff
        engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
        diff = list(engine.compare(want.splitlines(True),
                                   got.splitlines(True)))
        kind = 'ndiff with -expected +actual'
        diff = [line.rstrip() + '\n' for line in diff]
        self.fail('Differences (%s):\n' % kind + ''.join(diff))

    def assert_json(self, want, got=None):
        import doctest
        import simplejson
        if got is None:
            got = self.browser.contents
        data = simplejson.loads(got)
        self.assertEqual(want, data)
        return data
