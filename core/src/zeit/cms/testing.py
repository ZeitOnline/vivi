# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import BaseHTTPServer
import __future__
import contextlib
import copy
import gocept.jslint
import gocept.selenium.base
import gocept.selenium.ztk
import gocept.testing.assertion
import gocept.zcapatch
import inspect
import json
import logging
import pkg_resources
import random
import re
import string
import sys
import threading
import time
import transaction
import unittest2
import urllib2
import xml.sax.saxutils
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.app.wsgi
import zope.component
import zope.publisher.browser
import zope.security.management
import zope.security.testing
import zope.site.hooks
import zope.testbrowser.testing
import zope.testing.renormalizing


def ZCMLLayer(
        config_file, module=None, name=None, allow_teardown=True,
        product_config=None):
    if module is None:
        module = inspect.stack()[1][0].f_globals['__name__']
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

    def testSetUp(cls):
        cls.setup.setUp()
        # ``local_product_config`` contains mutable elements which tests may
        # modify. Create a copy to let setup restore the *original* config.
        cls.setup.local_product_config = copy.deepcopy(
            cls.setup.local_product_config)
        cls.setup.zca = gocept.zcapatch.Patches()

    def testTearDown(cls):
        try:
            connector = zope.component.getUtility(
                zeit.connector.interfaces.IConnector)
        except zope.component.interfaces.ComponentLookupError:
            pass
        else:
            connector._reset()
        cls.setup.zca.reset()
        zope.site.hooks.setSite(None)
        zope.security.management.endInteraction()
        cls.setup.tearDown()

    layer = type(name, (object,), dict(
        __module__=module,
        setUp=classmethod(setUp),
        tearDown=classmethod(tearDown),
        testSetUp=classmethod(testSetUp),
        testTearDown=classmethod(testTearDown),
    ))
    return layer


class HTTPServer(BaseHTTPServer.HTTPServer):
    # shutdown mechanism borrowed from gocept.selenium.static.HTTPServer

    _continue = True

    def __init__(self, *args):
        BaseHTTPServer.HTTPServer.__init__(self, *args)
        self.errors = []

    def handle_error(self, request, client_address):
        self.errors.append((request, client_address))

    def serve_until_shutdown(self):
        while self._continue:
            self.handle_request()

    def shutdown(self):
        self._continue = False
        # We fire a last request at the server in order to take it out of the
        # while loop in `self.serve_until_shutdown`.
        try:
            urllib2.urlopen(
                'http://%s:%s/die' % (self.server_name, self.server_port),
                timeout=1)
        except urllib2.URLError:
            # If the server is already shut down, we receive a socket error,
            # which we ignore.
            pass
        self.server_close()


def HTTPServerLayer(request_handler):
    """Factory for a layer which opens a HTTP port."""
    module = inspect.stack()[1][0].f_globals['__name__']
    port = random.randint(30000, 40000)

    def setUp(cls):
        server_address = ('localhost', port)
        cls.httpd = HTTPServer(server_address, request_handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_until_shutdown)
        cls.thread.daemon = True
        cls.thread.start()
        # Wait as it sometimes takes a while to get the server started.
        # XXX this is a little kludgy
        time.sleep(0.001)

    def tearDown(cls):
        cls.httpd.shutdown()
        cls.thread.join()

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
  source-banners file://${base}/content/banners.xml

  preview-prefix http://localhost/preview-prefix
  live-prefix http://localhost/live-prefix
  development-preview-prefix http://localhost/development-preview-prefix

  suggest-keyword-email-address none@testing
  suggest-keyword-real-name Dr. No
  whitelist-url file://${base}/tagging/tests/whitelist.xml
  keyword-configuration file://${base}/tagging/tests/keywords_config.xml
  breadcrumbs-use-common-metadata true
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

    def setUp(test):
        config = test.globs.get('product_config', {})
        __traceback_info__ = (config,)
        setup_product_config(config)

    layer = kw.pop('layer', cms_layer)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    kw['setUp'] = setUp
    globs = kw.setdefault('globs', {})
    globs['product_config'] = kw.pop('product_config', {})
    globs['with_statement'] = __future__.with_statement
    globs['getRootFolder'] = zope.app.testing.functional.getRootFolder
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)

    test = doctest.DocFileSuite(*paths, **kw)
    test.layer = layer

    return test


class RepositoryHelper(object):

    @property
    def repository(self):
        import zeit.cms.repository.interfaces
        with site(self.getRootFolder()):
            return zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)

    @repository.setter
    def repository(self, value):
        self.__dict__['repository'] = value


class FunctionalTestCaseCommon(
    unittest2.TestCase,
    gocept.testing.assertion.Ellipsis,
    gocept.testing.assertion.Exceptions,
    RepositoryHelper):

    layer = cms_layer
    product_config = {}

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return zope.app.testing.functional.FunctionalTestSetup().\
            getRootFolder()

    @property
    def zca(self):
        return zope.app.testing.functional.FunctionalTestSetup().zca

    def setUp(self):
        super(FunctionalTestCaseCommon, self).setUp()
        setup_product_config(self.product_config)


class FunctionalTestCase(FunctionalTestCaseCommon):

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        zope.site.hooks.setSite(self.getRootFolder())
        self.principal = create_interaction(u'zope.user')


class SeleniumTestCase(gocept.selenium.base.TestCase,
                       FunctionalTestCaseCommon):

    layer = selenium_layer
    skin = 'cms'
    log_errors = False
    log_errors_ignore = ()
    level = 2

    TIMEOUT = 10

    window_width = 1100
    window_height = 600

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        # XXX waiting for a version of gocept.selenium that handles timeouts
        # consistently (#10750)
        self.layer.selenium.setTimeout(self.TIMEOUT*1000)
        self.layer.selenium.selenium.set_timeout(self.TIMEOUT*1000)

        # XXX The following 5 lines are copied from
        # gocept.selenium.ztk.TestCase in order to avoid inheriting from
        # zope.app.testing.functional.TestCase.
        db = zope.app.testing.functional.FunctionalTestSetup().db
        application = self.layer.http.application
        assert isinstance(application, zope.app.wsgi.WSGIPublisherApplication)
        factory = type(application.requestFactory)
        application.requestFactory = factory(db)

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

        self.original_windows = set(self.selenium.getAllWindowNames())
        self.original_width = self.selenium.getEval('window.outerWidth')
        self.original_height = self.selenium.getEval('window.outerHeight')
        self.set_window_size(self.window_width, self.window_height)

    def tearDown(self):
        super(SeleniumTestCase, self).tearDown()
        if self.log_errors:
            logging.root.removeHandler(self.log_handler)
            logging.root.setLevel(self.old_log_level)

        current_windows = set(self.selenium.getAllWindowNames())
        for window in current_windows - self.original_windows:
            self.selenium.selectWindow(window)
            self.selenium.close()
        self.selenium.selectWindow()

        self.set_window_size(self.original_width, self.original_height)

    def set_window_size(self, width, height):
        s = self.selenium
        s.getEval('window.resizeTo(%s, %s)' % (width, height))
        s.waitForEval('window.outerWidth', str(width))
        s.waitForEval('window.outerHeight', str(height))

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

    setup_globals = """\
        var window = selenium.browserbot.getCurrentWindow();
        var document = window.document;
        var zeit = window.zeit;
        """

    def eval(self, text):
        return self.selenium.getEval(self.setup_globals + text)

    def wait_for_condition(self, text):
        self.selenium.waitForCondition(self.setup_globals + """\
        Boolean(%s);
        """ % text)

    def wait_for_dotted_name(self, dotted_name):
        partial = []
        for part in dotted_name.split('.'):
            partial.append(part)
            self.wait_for_condition('.'.join(partial))


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


# XXX use zope.publisher.testing for the following two
def create_interaction(name=u'zope.user'):
    principal = zope.security.testing.Principal(
        name, groups=['zope.Authenticated'], description=u'test@example.com')
    request = zope.publisher.browser.TestRequest()
    request.setPrincipal(principal)
    zope.security.management.newInteraction(request)
    return principal


@contextlib.contextmanager
def interaction(principal_id=u'zope.user'):
    if zope.security.management.queryInteraction():
        # There already is an interaction. Great. Leave it alone.
        yield
    else:
        principal = create_interaction(principal_id)
        yield principal
        zope.security.management.endInteraction()


# XXX use zope.component.testing.site instead
@contextlib.contextmanager
def site(root):
    old_site = zope.site.hooks.getSite()
    zope.site.hooks.setSite(root)
    yield
    zope.site.hooks.setSite(old_site)


class BrowserAssertions(gocept.testing.assertion.Ellipsis):

    # XXX backwards-compat method signature for existing tests, should probably
    # be removed at some point
    def assert_ellipsis(self, want, got=None):
        if got is None:
            got = self.browser.contents
        self.assertEllipsis(want, got)

    def assert_json(self, want, got=None):
        if got is None:
            got = self.browser.contents
        data = json.loads(got)
        self.assertEqual(want, data)
        return data


class BrowserTestCase(FunctionalTestCaseCommon, BrowserAssertions):

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')


class JSLintTestCase(gocept.jslint.TestCase):

    options = (gocept.jslint.TestCase.options +
               ('evil',
                'eqnull',
                'multistr',
                'sub',
                'undef',
                'browser',
                'jquery',
                'devel'
                ))
    predefined = (
        'zeit', 'gocept',
        'application_url', 'context_url',
        'DOMParser', 'escape', 'unescape', 'getSelection',
        'jsontemplate',
        'MochiKit', '$$', 'forEach', 'filter', 'map', 'extend', 'bind',
        'log', 'repr', 'logger', 'logDebug', 'logError',  # XXX
        'DIV', 'A', 'UL', 'LI', 'INPUT', 'IMG', 'SELECT', 'OPTION', 'BUTTON',
        'SPAN',
        'isNull', 'isUndefined', 'isUndefinedOrNull',
        )

    ignore = (
        "Don't make functions within a loop",
        "Expected an identifier and instead saw 'import'",
        "Use '===' to compare with",
        "Use '!==' to compare with",
        "Missing radix parameter",
        "Bad line breaking",
        )
