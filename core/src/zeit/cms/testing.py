from zope.testing import doctest
import BaseHTTPServer
import __future__
import contextlib
import copy
import gocept.httpserverlayer.wsgi
import gocept.jslint
import gocept.selenium
import gocept.testing.assertion
import gocept.zcapatch
import inspect
import json
import logging
import os
import pkg_resources
import plone.testing
import pytest
import random
import re
import socket
import sys
import threading
import time
import transaction
import unittest
import urllib2
import xml.sax.saxutils
import zeit.cms.workflow.mock
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.app.wsgi
import zope.component
import zope.i18n.interfaces
import zope.publisher.browser
import zope.security.management
import zope.security.testing
import zope.site.hooks
import zope.testbrowser.testing
import zope.testing.renormalizing


class ZCMLLayer(plone.testing.Layer):

    def __init__(self, config_file, product_config=None,
                 name='ZCMLLayer', module=None):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        if not config_file.startswith('/'):
            config_file = pkg_resources.resource_filename(module, config_file)
        self.config_file = config_file
        self.product_config = product_config
        super(ZCMLLayer, self).__init__(name=name, module=module)

    def setUp(self):
        # This calls zope.testing.cleanup.cleanUp()
        self.setup = zope.app.testing.functional.FunctionalTestSetup(
            self.config_file, product_config=self.product_config)
        self['functional_setup'] = self.setup

    def tearDown(self):
        # This calls zope.testing.cleanup.cleanUp()
        self.setup.tearDownCompletely()
        del self['functional_setup']

    def testSetUp(self):
        self.setup.setUp()
        # ``local_product_config`` contains mutable elements which tests may
        # modify. Create a copy to let setup restore the *original* config.
        self.setup.local_product_config = copy.deepcopy(
            self.setup.local_product_config)
        self.setup.zca = gocept.zcapatch.Patches()

    def testTearDown(self):
        # We must *not* call zope.testing.cleanup.cleanUp() here, since that
        # (among many other things) empties the zope.component registry.

        # XXX We seem to collect unrelated tearDown things here, those should
        # probably go into their own separate layers.
        try:
            connector = zope.component.getUtility(
                zeit.connector.interfaces.IConnector)
        except zope.component.interfaces.ComponentLookupError:
            pass
        else:
            connector._reset()

        zeit.cms.workflow.mock.reset()

        self.setup.zca.reset()
        zope.site.hooks.setSite(None)
        zope.security.management.endInteraction()
        self.setup.tearDown()


class WSGILayer(plone.testing.Layer):

    def setUp(self):
        db = zope.app.testing.functional.FunctionalTestSetup().db
        self['zope_app'] = zope.app.wsgi.WSGIPublisherApplication(db)
        self['wsgi_app'] = zeit.cms.application.APPLICATION.setup_pipeline(
            self['zope_app'])

    def testSetUp(self):
        # Switch database to the currently active DemoStorage.
        # Adapted from gocept.httpserverlayer.zopeapptesting.TestCase
        db = zope.app.testing.functional.FunctionalTestSetup().db
        application = self['zope_app']
        factory = type(application.requestFactory)
        application.requestFactory = factory(db)

    def tearDown(self):
        del self['wsgi_app']
        del self['zope_app']


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
        except (socket.timeout, urllib2.URLError):
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


cms_product_config = """\
<product-config zeit.cms>
  source-access file://{base}/content/access.xml
  source-serie file://{base}/content/serie.xml
  source-navigation file://{base}/content/navigation.xml
  source-keyword file://{base}/content/zeit-ontologie-prism.xml
  source-products file://{base}/content/products.xml
  source-badges file://{base}/asset/badges.xml
  source-banners file://{base}/content/banners.xml
  source-channels file://{base}/content/navigation.xml
  source-storystreams file://{base}/content/storystreams.xml
  source-printressorts file://{base}/content/print-ressorts.xml

  preview-prefix http://localhost/preview-prefix
  live-prefix http://localhost/live-prefix
  friebert-wc-preview-prefix /wcpreview

  suggest-keyword-email-address none@testing
  suggest-keyword-real-name Dr. No
  whitelist-url file://{base}/tagging/tests/fixtures/whitelist.xml
  keyword-configuration file://{base}/tagging/tests/fixtures/kw_config.xml
  trisolute-url file://{base}/tagging/tests/fixtures/googleNewsTopics.json
  trisolute-ressort-url file://{base}/tagging/tests/fixtures/tris-ressorts.xml
  breadcrumbs-use-common-metadata true

  task-queue-async events
  cache-expiration-config 600
  celery-config /dev/null
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


ZCML_LAYER = ZCMLLayer('ftesting.zcml', product_config=cms_product_config)
WSGI_LAYER = WSGILayer(name='WSGILayer', bases=(ZCML_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>'),
    (re.compile('0x[0-9a-f]+'), "0x..."),
    (re.compile(r'/\+\+noop\+\+[0-9a-f]+'), ''),
    (re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
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

    layer = kw.pop('layer', ZCML_LAYER)
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
        unittest.TestCase,
        gocept.testing.assertion.Ellipsis,
        gocept.testing.assertion.Exceptions,
        RepositoryHelper):

    product_config = {}

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return self.layer['functional_setup'].getRootFolder()

    @property
    def zca(self):
        return self.layer['functional_setup'].zca

    def setUp(self):
        super(FunctionalTestCaseCommon, self).setUp()
        setup_product_config(self.product_config)


class FunctionalTestCase(FunctionalTestCaseCommon):

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        zope.site.hooks.setSite(self.getRootFolder())
        self.principal = create_interaction(u'zope.user')


# XXX We should subclass instead of monkey-patch, but then I'd have
# to change all the layer declarations in the zeit.* packages, sigh.

def selenium_setup_authcache(self):
    # NOTE: Massively kludgy workaround. It seems that Firefox has a timing
    # issue with HTTP auth and AJAX calls: if you open a page that requires
    # auth and has AJAX calls to further pages that require the same auth,
    # sometimes those AJAX calls come back as 401 (nothing to do with
    # Selenium, we've seen this against the actual server).
    #
    # It seems that opening a page and then giving it a little time
    # to settle in is enough to work around this issue.

    original_setup(self)
    s = self['selenium']
    self['http_auth_cache'] = True
    # XXX It seems something is not ready immediately?!??
    s.pause(1000)
    # XXX Credentials are duplicated from SeleniumTestCase.open().
    s.open('http://user:userpw@%s/++skin++vivi/@@test-setup-auth'
           % self['http_address'])
    # We don't really know how much time the browser needs until it's
    # satisfied, or how we could determine this.
    s.pause(1000)
original_setup = gocept.selenium.webdriver.WebdriverSeleneseLayer.setUp
gocept.selenium.webdriver.WebdriverSeleneseLayer.setUp = (
    selenium_setup_authcache)


def selenium_teardown_authcache(self):
    original_teardown(self)
    del self['http_auth_cache']
original_teardown = gocept.selenium.webdriver.WebdriverSeleneseLayer.tearDown
gocept.selenium.webdriver.WebdriverSeleneseLayer.tearDown = (
    selenium_teardown_authcache)


@pytest.mark.slow
class SeleniumTestCase(gocept.selenium.WebdriverSeleneseTestCase,
                       FunctionalTestCase):

    skin = 'cms'
    log_errors = False
    log_errors_ignore = ()
    level = 2

    TIMEOUT = int(os.environ.get('ZEIT_SELENIUM_TIMEOUT', 10))

    window_width = 1100
    window_height = 600

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        self.layer['selenium'].setTimeout(self.TIMEOUT * 1000)

        if self.log_errors:
            with site(self.getRootFolder()):
                error_log = zope.component.getUtility(
                    zope.error.interfaces.IErrorReportingUtility)
                error_log.copy_to_zlog = True
                error_log._ignored_exceptions = self.log_errors_ignore
            self.log_handler = logging.StreamHandler(sys.stdout)
            logging.root.addHandler(self.log_handler)
            self.old_log_level = logging.root.level
            logging.root.setLevel(logging.WARN)
            transaction.commit()

        self.original_windows = set(self.selenium.getAllWindowIds())
        self.original_width = self.selenium.getEval('window.outerWidth')
        self.original_height = self.selenium.getEval('window.outerHeight')
        self.selenium.setWindowSize(self.window_width, self.window_height)
        self.eval('window.localStorage.clear()')

    def tearDown(self):
        super(SeleniumTestCase, self).tearDown()
        if self.log_errors:
            logging.root.removeHandler(self.log_handler)
            logging.root.setLevel(self.old_log_level)

        current_windows = set(self.selenium.getAllWindowIds())
        for window in current_windows - self.original_windows:
            self.selenium.selectWindow(window)
            self.selenium.close()
        self.selenium.selectWindow()

        self.selenium.setWindowSize(self.original_width, self.original_height)
        # open a neutral page to stop all pending AJAX requests
        self.open('/@@test-setup-auth')

    def open(self, path, auth='user:userpw'):
        if auth:
            auth += '@'
        self.selenium.open(
            'http://%s%s/++skin++%s%s' % (
                auth, self.selenium.server, self.skin, path))

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))

    js_globals = """\
        var document = window.document;
        var zeit = window.zeit;
    """

    def eval(self, text):
        return self.selenium.selenium.execute_script(
            self.js_globals + 'return ' + text)

    def wait_for_condition(self, text):
        self.selenium.waitForCondition(self.js_globals + """\
        return Boolean(%s);
        """ % text)

    def wait_for_dotted_name(self, dotted_name):
        partial = []
        for part in dotted_name.split('.'):
            partial.append(part)
            self.wait_for_condition('.'.join(partial))

    def add_by_autocomplete(self, text, widget):
        s = self.selenium
        s.type(widget, text)
        autocomplete_item = 'css=.ui-menu-item a'
        s.waitForElementPresent(autocomplete_item)
        s.waitForVisible(autocomplete_item)
        s.click(autocomplete_item)
        s.waitForNotVisible('css=.ui-menu')


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
def create_interaction(name='zope.user'):
    name = unicode(name)  # XXX At least zope.dublincore requires unicode...
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


class TestCatalog(object):

    zope.interface.implements(zope.i18n.interfaces.IGlobalMessageCatalog)
    language = 'tt'
    messages = {}

    def queryMessage(self, msgid, default=None):
        return self.messages.get(msgid, default)

    getMessage = queryMessage

    def getIdentifier(self):
        return 'test'

    def reload(self):
        pass


def copy_inherited_functions(base, locals):
    """py.test annotates the test function object with data, e.g. required
    fixtures. Normal inheritance means that there is only *one* function object
    (in the base class), which means for example that subclasses cannot specify
    different layers, since they would all aggregate on that one function
    object, which would be completely wrong.

    Usage: copy_inherited_functions(BaseClass, locals())
    """
    def make_delegate(name):
        def delegate(self):
            return getattr(super(type(self), self), name)()
        return delegate

    for name in dir(base):
        if not name.startswith('test_'):
            continue
        locals[name] = make_delegate(name)


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

    login_as = 'user:userpw'

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic %s' % self.login_as)


# These ugly names are due to two reasons:
# 1. zeit.cms.testing contains both general test mechanics *and*
#    specific test infrastructure/layers for zeit.cms itself
# 2. pytest does not allow for subclassing a TestCase and changing its layer
#    (for the same reason as copy_inherited_functions above).

class ZeitCmsTestCase(FunctionalTestCase):

    layer = ZCML_LAYER


class ZeitCmsBrowserTestCase(BrowserTestCase):

    layer = ZCML_LAYER


class JSLintTestCase(gocept.jslint.TestCase):

    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/true')

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
        'DOMParser', 'escape', 'unescape',
        'jsontemplate',
        'MochiKit', '$$', 'forEach', 'filter', 'map', 'extend', 'bind',
        'log', 'repr', 'logger', 'logDebug', 'logError',  # XXX
        'DIV', 'A', 'UL', 'LI', 'INPUT', 'IMG', 'SELECT', 'OPTION', 'BUTTON',
        'SPAN', 'LABEL',
        'isNull', 'isUndefined', 'isUndefinedOrNull',
        'Uri',
        '_',  # js.underscore
    )

    ignore = (
        "Don't make functions within a loop",
        "Expected an identifier and instead saw 'import'",
        "Use '===' to compare with",
        "Use '!==' to compare with",
        "Missing radix parameter",
        "Bad line breaking",
        "Expected an assignment or function call and instead"
        " saw an expression",
    )
