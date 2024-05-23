from io import StringIO
from urllib.parse import urljoin
import base64
import contextlib
import copy
import doctest
import importlib.resources
import inspect
import json
import logging
import os
import re
import sys
import tempfile
import threading
import unittest
import xml.sax.saxutils

from selenium.webdriver.common.by import By
import celery.contrib.testing.app
import celery.contrib.testing.worker
import celery_longterm_scheduler
import gocept.httpserverlayer.custom
import gocept.jslint
import gocept.selenium
import gocept.selenium.wd_selenese
import gocept.testing.assertion
import kombu
import lxml.cssselect
import lxml.etree
import lxml.html
import opentelemetry.util.http
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import pytest
import selenium.webdriver
import transaction
import waitress.server
import webtest.lint
import ZODB
import ZODB.DemoStorage
import zope.app.appsetup.product
import zope.app.publication.zopepublication
import zope.app.wsgi
import zope.component
import zope.component.hooks
import zope.error.interfaces
import zope.i18n.interfaces
import zope.interface
import zope.publisher.browser
import zope.security.management
import zope.security.proxy
import zope.security.testing
import zope.testbrowser.browser
import zope.testing.renormalizing

import zeit.cms.application
import zeit.cms.celery
import zeit.cms.wsgi
import zeit.cms.zope
import zeit.connector.interfaces
import zeit.connector.mock


class LoggingLayer(plone.testing.Layer):
    def setUp(self):
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('zeit').setLevel(logging.DEBUG)
        logging.getLogger('zeit.cms.repository').setLevel(logging.INFO)
        logging.getLogger('selenium').setLevel(logging.INFO)
        logging.getLogger('bugsnag').setLevel(logging.FATAL)
        logging.getLogger('waitress').setLevel(logging.ERROR)


LOGGING_LAYER = LoggingLayer()


class CeleryEagerLayer(plone.testing.Layer):
    def setUp(self):
        zeit.cms.celery.CELERY.conf.task_always_eager = True

    def tearDown(self):
        zeit.cms.celery.CELERY.conf.task_always_eager = False


CELERY_EAGER_LAYER = CeleryEagerLayer()


class ProductConfigLayer(plone.testing.Layer):
    DELETE = object()

    def __init__(
        self, config, package=None, patches=None, name='ConfigLayer', module=None, bases=None
    ):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        super().__init__(name=name, module=module, bases=bases)
        if not package:
            package = '.'.join(module.split('.')[:-1])
        self.package = package
        if isinstance(config, str):  # BBB
            config = self.loadConfiguration(config, package)
        self.config = config
        self.patches = patches or {}

    def loadConfiguration(self, text, package):
        return zope.app.appsetup.product.loadConfiguration(StringIO(text))[package]

    def setUp(self):
        self.previous = {}

        product = zope.app.appsetup.product.getProductConfiguration(self.package)
        if product:
            self.previous[self.package] = copy.deepcopy(product)
        zope.app.appsetup.product.setProductConfiguration(self.package, copy.deepcopy(self.config))

        for package, config in self.patches.items():
            previous = self.previous[package] = {}
            product = zope.app.appsetup.product.getProductConfiguration(package)
            for key in config:
                if product and key in product:
                    previous[key] = copy.deepcopy(product[key])
                else:
                    previous[key] = self.DELETE
            self._update(package, config)

    def tearDown(self):
        zope.app.appsetup.product.setProductConfiguration(self.package, None)
        for package, config in self.previous.items():
            self._update(package, config)

    def testSetUp(self):
        zope.app.appsetup.product.setProductConfiguration(self.package, copy.deepcopy(self.config))
        for package, config in self.patches.items():
            self._update(package, config)

    def _update(self, package, config):
        product = zope.app.appsetup.product.getProductConfiguration(package)
        if product is None:
            zope.app.appsetup.product.setProductConfiguration(package, {})
            product = zope.app.appsetup.product.getProductConfiguration(package)
        for key, value in config.items():
            if value is self.DELETE:
                product.pop(key, None)
            else:
                product[key] = copy.deepcopy(value)


class ZCMLLayer(plone.testing.Layer):
    defaultBases = (LOGGING_LAYER,)

    def __init__(
        self, config_file='ftesting.zcml', features=(), name='ZCMLLayer', module=None, bases=()
    ):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        package, _ = module.rsplit('.', 1)
        if not config_file.startswith('/'):
            config_file = str((importlib.resources.files(package) / config_file))
        self.config_file = config_file
        self.features = features
        super().__init__(name=name, module=module, bases=self.defaultBases + bases)

    def setUp(self):
        self['zcaRegistry'] = plone.testing.zca.pushGlobalRegistry()
        self.assert_non_browser_modules_have_no_browser_zcml()
        self['zcaContext'] = zeit.cms.zope._load_zcml(self.config_file, self.features)

    def assert_non_browser_modules_have_no_browser_zcml(self):
        # Caveat emptor: This whole method is a bunch of heuristics, but
        # hopefully they are useful.
        for browser in ['browser', 'json', 'xmlrpc']:
            if '.' + browser in self.__module__:
                return

        if self.__module__.startswith('zeit.addcentral'):
            # XXX This is a historical edge case.
            return

        configure_zcml = os.path.dirname(self.config_file) + '/configure.zcml'
        if not os.path.exists(configure_zcml):
            return  # be defensive

        with open(configure_zcml) as f:
            zcml = f.read().splitlines()
        for directive in ['namespaces.zope.org/browser', 'gocept:pagelet']:
            for i, line in enumerate(zcml):
                if directive in line:
                    raise AssertionError(
                        'Browser-specific directive found in %s\n'
                        '    %s: %s' % (configure_zcml, i, line)
                    )

    def tearDown(self):
        plone.testing.zca.popGlobalRegistry()
        del self['zcaRegistry']
        # We also need to clean up various other Zope registries here
        # (permissions, tales expressions etc.), but the zope.testing mechanism
        # to do that unfortunately also includes clearing the product config,
        # which we do NOT want.
        product = zope.app.appsetup.product.saveConfiguration()
        zope.testing.cleanup.cleanUp()
        zope.app.appsetup.product.restoreConfiguration(product)

    def testSetUp(self):
        self['zcaRegistry'] = plone.testing.zca.pushGlobalRegistry()

    def testTearDown(self):
        self['zcaRegistry'] = plone.testing.zca.popGlobalRegistry()


class AdditionalZCMLLayer(plone.testing.Layer):
    """Requires a ZCMLLayer instance in the layer hierarchy above it."""

    def __init__(
        self,
        package=None,
        config_file='configure.zcml',
        name='AdditionalZCMLLayer',
        module=None,
        bases=(),
    ):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        if package is None:
            package, _ = module.rsplit('.', 1)
        if not config_file.startswith('/'):
            config_file = str((importlib.resources.files(package) / config_file))
        self.config_file = config_file
        super().__init__(name=name, module=module, bases=self.defaultBases + bases)

    def setUp(self):
        self['zcaRegistryAdd'] = plone.testing.zca.pushGlobalRegistry()
        zope.configuration.xmlconfig.include(self['zcaContext'], file=self.config_file)
        self['zcaContext'].execute_actions()

    def tearDown(self):
        plone.testing.zca.popGlobalRegistry()
        del self['zcaRegistryAdd']


class ZODBLayer(plone.testing.Layer):
    def setUp(self):
        self['zodbDB-layer'] = ZODB.DB(ZODB.DemoStorage.DemoStorage(name=self.__name__ + '-layer'))

    def tearDown(self):
        self['zodbDB-layer'].close()
        del self['zodbDB-layer']

    def testSetUp(self):
        self['zodbDB'] = plone.testing.zodb.stackDemoStorage(
            self['zodbDB-layer'], name=self.__name__
        )
        self['zodbConnection'] = self['zodbDB'].open()

    def testTearDown(self):
        transaction.abort()
        self['zodbConnection'].close()
        del self['zodbConnection']
        self['zodbDB'].close()
        del self['zodbDB']


class ResetMocks:
    """ZCA event for pluggable reset handlers that run on testTearDown."""


class MockResetLayer(plone.testing.Layer):
    event = (zope.interface.providedBy(ResetMocks()),)

    def testTearDown(self):
        registry = zope.component.getSiteManager().adapters
        # Like zope.event.notify(), but expects handlers to take no parameters
        # (instead of the event object)
        for func in registry.subscriptions(self.event, None):
            func()


MOCK_RESET_LAYER = MockResetLayer()


def reset_connector():
    connector = zope.component.queryUtility(zeit.connector.interfaces.IConnector)
    if isinstance(connector, zeit.connector.mock.Connector):
        connector._reset()


class ZopeLayer(plone.testing.Layer):
    defaultBases = (
        CELERY_EAGER_LAYER,
        MOCK_RESET_LAYER,
    )

    def __init__(self, name='ZopeLayer', module=None, bases=()):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        super().__init__(
            name=name,
            module=module,
            # This is a bit kludgy. We need an individual ZODB layer per ZCML
            # file (so e.g. different install generations are isolated), but
            # we don't really want to have to create one per package.
            bases=self.defaultBases + bases + (ZODBLayer(),),
        )

    def setUp(self):
        zope.event.notify(zope.processlifetime.DatabaseOpened(self['zodbDB-layer']))
        transaction.commit()
        with self.rootFolder(self['zodbDB-layer']):
            pass
        self['rootFolder'] = self.rootFolder

    def tearDown(self):
        del self['rootFolder']

    @contextlib.contextmanager
    def rootFolder(self, db):
        """Helper for other layers to access the ZODB.

        We cannot leave a connection open after setUp, since it will join the
        transactions that happen during the tests, which breaks because the
        same DB is then joined twice. Thus we have to take care and close it
        each time.
        """
        connection = db.open()
        root = connection.root()[zope.app.publication.zopepublication.ZopePublication.root_name]
        self._set_current_zca(root)
        yield root
        transaction.commit()
        connection.close()

    def testSetUp(self):
        self['zodbApp'] = self['zodbConnection'].root()[
            zope.app.publication.zopepublication.ZopePublication.root_name
        ]
        self._set_current_zca(self['zodbApp'])
        transaction.commit()

    def testTearDown(self):
        zope.component.hooks.setSite(None)
        zope.security.management.endInteraction()
        del self['zodbApp']

    def _set_current_zca(self, root):
        site = zope.component.getSiteManager(root)
        site.__bases__ = (self['zcaRegistry'],)


class WSGILayer(plone.testing.Layer):
    def __init__(self, name='WSGILayer', module=None, bases=None):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        super().__init__(name=name, module=module, bases=bases)

    def setUp(self):
        self['zope_app'] = zope.app.wsgi.WSGIPublisherApplication(self['zodbDB-layer'])
        self['wsgi_app'] = zeit.cms.wsgi.wsgi_pipeline(
            self['zope_app'],
            [
                ('prometheus', 'call:zeit.cms.application:prometheus_filter'),
                ('fanstatic', 'call:fanstatic:make_fanstatic'),
            ],
            {
                'fanstatic.' + key: value
                for key, value in zeit.cms.application.FANSTATIC_SETTINGS.items()
            },
        )
        self['wsgi_app'] = zeit.cms.application.OpenTelemetryMiddleware(
            self['wsgi_app'],
            opentelemetry.util.http.ExcludeList(zeit.cms.application.Application.tracing_exclude),
        )

    def testSetUp(self):
        # Switch database to the currently active DemoStorage.
        # Adapted from gocept.httpserverlayer.zopeapptesting.TestCase
        application = self['zope_app']
        factory = type(application.requestFactory)
        application.requestFactory = factory(self['zodbDB'])

    def tearDown(self):
        del self['wsgi_app']
        del self['zope_app']


class CeleryWorkerLayer(plone.testing.Layer):
    """Sets up a thread-layerd celery worker.

    Modeled after celery.contrib.testing.pytest.celery_session_worker and
    celery_session_app.
    """

    queues = (
        'default',
        'publish_homepage',
        'publish_highprio',
        'publish_lowprio',
        'publish_default',
        'publish_timebased',
        'webhook',
    )
    default_queue = 'default'

    def __init__(self, name='CeleryLayer', module=None, bases=None):
        if module is None:
            module = inspect.stack()[1][0].f_globals['__name__']
        super().__init__(name=name, module=module, bases=bases)

    def setUp(self):
        self['celery_app'] = zeit.cms.celery.CELERY
        self['celery_previous_config'] = dict(self['celery_app'].conf)

        self['celery_app'].conf.update(celery.contrib.testing.app.DEFAULT_TEST_CONFIG)
        self['celery_app'].conf.update(
            {
                'task_always_eager': False,
                'task_create_missing_queues': False,
                'task_default_queue': self.default_queue,
                'task_queues': [kombu.Queue(q) for q in self.queues],
                'task_send_sent_event': True,  # So we can inspect routing in tests
                'longterm_scheduler_backend': 'memory://',
                'TESTING': True,
                'broker_connection_retry_on_startup': True,  # Avoid deprecation warning
                'ZODB': self['zodbDB-layer'],
            }
        )
        self.reset_celery_app()

        self['celery_worker'] = celery.contrib.testing.worker.start_worker(self['celery_app'])
        self['celery_worker'].__enter__()

    def reset_celery_app(self):
        # Reset cached_property values that depend on app.conf values, after
        # config has been changed.
        cls = type(self['celery_app'])
        for name in dir(cls):
            prop = getattr(cls, name)
            if isinstance(prop, kombu.utils.objects.cached_property):
                self['celery_app'].__dict__.pop(name, None)
        # Kludgy way to reset `app.backend`
        self['celery_app']._local = threading.local()

    def testSetUp(self):
        # Switch database to the currently active DemoStorage,
        # see zeit.cms.testing.WSGILayer.testSetUp().
        self['celery_app'].conf['ZODB'] = self['zodbDB']

        celery_longterm_scheduler.get_scheduler(self['celery_app']).backend.__init__(None, None)

    def tearDown(self):
        self['celery_worker'].__exit__(None, None, None)
        del self['celery_worker']

        # This should remove any config additions made by us.
        self['celery_app'].conf.clear()
        self['celery_app'].conf.update(self['celery_previous_config'])
        del self['celery_previous_config']
        self.reset_celery_app()

        del self['celery_app']


# celery.contrib.testing.worker expects a 'ping' task, so it can check that the
# worker is running properly.
@zeit.cms.celery.task(name='celery.ping')
def celery_ping():
    return 'pong'


class RecordingRequestHandler(gocept.httpserverlayer.custom.RequestHandler):
    response_code = 200
    response_headers = {}
    response_body = '{}'

    def do_GET(self):
        length = int(self.headers.get('content-length', 0))
        self.requests.append(
            {
                'verb': self.command,
                'path': self.path,
                'headers': self.headers,
                'body': self.rfile.read(length).decode('utf-8') if length else None,
            }
        )
        self.send_response(self._next('response_code'))
        for key, value in self._next('response_headers').items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(self._next('response_body').encode('utf-8'))

    def _next(self, name):
        result = getattr(self, name)
        if isinstance(result, list):
            result = result.pop(0)
        return result

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class HTTPLayer(gocept.httpserverlayer.custom.Layer):
    def testSetUp(self):
        super().testSetUp()
        self['request_handler'].requests = []
        self['request_handler'].response_headers = {}
        self['request_handler'].response_body = '{}'
        self['request_handler'].response_code = 200


cms_product_config = """\
<product-config zeit.cms>
  environment testing

  source-access file://{here}/content/access.xml
  source-serie file://{here}/content/serie.xml
  source-ressorts file://{here}/content/ressorts.xml
  source-keyword file://{here}/content/zeit-ontologie-prism.xml
  source-products file://{here}/content/products.xml
  source-badges file://{here}/asset/badges.xml
  source-channels file://{here}/content/ressorts.xml
  source-printressorts file://{here}/content/print-ressorts.xml
  source-manual file://{here}/content/manual.xml

  config-retractlog file://{here}/retractlog/retractlog.xml

  checkout-lock-timeout 3600
  checkout-lock-timeout-temporary 30

  preview-prefix http://localhost/preview-prefix/
  live-prefix http://localhost/live-prefix/
  image-live-prefix http://localhost/img-live-prefix/
  friebert-wc-preview-prefix /wcpreview

  breadcrumbs-use-common-metadata true

  cache-regions config, feature, newsimport, dav
  cache-expiration-config 600
  cache-expiration-feature 15
  cache-expiration-newsimport 1
  cache-expiration-dav 0
  feature-toggle-source file://{here}/content/feature-toggle.xml

  sso-cookie-name-prefix my_sso_
  sso-cookie-domain
  sso-expiration 300
  sso-algorithm RS256
  sso-private-key-file {here}/tests/sso-private.pem

  source-api-mapping product=zeit.cms.content.sources.ProductSource
  # We just need a dummy XML file
  checkin-webhook-config file://{here}/content/access.xml
</product-config>
""".format(here=importlib.resources.files(__package__))


CONFIG_LAYER = ProductConfigLayer(
    cms_product_config,
    patches={
        'zeit.connector': {
            'repository-path': str((importlib.resources.files('zeit.connector') / 'testcontent'))
        }
    },
)
ZCML_LAYER = ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = WSGILayer(bases=(ZOPE_LAYER,))


# Layer API modelled after gocept.httpserverlayer.wsgi
class WSGIServerLayer(plone.testing.Layer):
    port = 0  # choose automatically

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.wsgi_app = None

    @property
    def wsgi_app(self):
        return self.get('wsgi_app', self._wsgi_app)

    @wsgi_app.setter
    def wsgi_app(self, value):
        self._wsgi_app = value

    @property
    def host(self):
        return os.environ.get('GOCEPT_HTTP_APP_HOST', 'localhost')

    def setUp(self):
        self['httpd'] = waitress.server.create_server(
            self.wsgi_app, host=self.host, port=0, ipv6=False, clear_untrusted_proxy_headers=True
        )

        if isinstance(self['httpd'], waitress.server.MultiSocketServer):
            self['http_host'] = self['httpd'].effective_listen[0][0]
            self['http_port'] = self['httpd'].effective_listen[0][1]
        else:
            self['http_host'] = self['httpd'].effective_host
            self['http_port'] = self['httpd'].effective_port
        self['http_address'] = '%s:%s' % (self['http_host'], self['http_port'])

        self['httpd_thread'] = threading.Thread(target=self._run)
        self['httpd_thread'].daemon = True
        self['httpd_thread'].start()

    def _run(self):
        try:
            self['httpd'].run()
        except Exception:
            # Ignore "bad file descriptor" exceptions during tearDown
            logging.getLogger('waitress').warning(
                'Suppressed exception to keep thread from crashing'
                ' (most probably during shutdown anyway)',
                exc_info=True,
            )

    def tearDown(self):
        self['httpd'].close()

        self['httpd_thread'].join(5)
        if self['httpd_thread'].is_alive():
            raise RuntimeError('WSGI server could not be shut down')

        del self['httpd']
        del self['httpd_thread']

        del self['http_host']
        del self['http_port']
        del self['http_address']


HTTP_LAYER = WSGIServerLayer(name='HTTPLayer', bases=(WSGI_LAYER,))


class WebdriverLayer(gocept.selenium.WebdriverLayer):
    def get_firefox_webdriver_args(self):
        options = selenium.webdriver.FirefoxOptions()
        if self['headless']:
            options.add_argument('-headless')

        profile_path = os.environ.get('GOCEPT_WEBDRIVER_FF_PROFILE')
        if profile_path:
            options.set_preference('profile', profile_path)

        # The default 'info' is still way too verbose
        options.log.level = 'error'
        binary = os.environ.get('GOCEPT_WEBDRIVER_FF_BINARY')
        if binary:
            options.binary_location = binary
        return {'options': options}

    def _stop_selenium(self):
        super()._stop_selenium()
        if 'seleniumrc' not in self:
            return
        self['seleniumrc'].command_executor._conn.clear()
        binary = getattr(self['seleniumrc'], 'binary', None)
        if binary is not None:
            binary._log_file.close()


WD_LAYER = WebdriverLayer(name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,)
)


checker = zope.testing.renormalizing.RENormalizing(
    [
        (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>'),
        (re.compile('0x[0-9a-f]+'), '0x...'),
        (re.compile(r'/\+\+noop\+\+[0-9a-f]+'), ''),
        (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<GUID>'),
    ]
)


def remove_exception_module(msg):
    """Copy&paste so we keep the exception message and support multi-line."""
    start, end = 0, len(msg)
    name_end = msg.find(':', 0, end)
    i = msg.rfind('.', 0, name_end)
    if i >= 0:
        start = i + 1
    return msg[start:end]


doctest._strip_exception_details = remove_exception_module


optionflags = (
    doctest.REPORT_NDIFF
    + doctest.NORMALIZE_WHITESPACE
    + doctest.ELLIPSIS
    + doctest.IGNORE_EXCEPTION_DETAIL
)


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', WSGI_LAYER)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = lambda: layer['zodbApp']
    globs['layer'] = layer
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)
    kw['encoding'] = 'utf-8'

    test = doctest.DocFileSuite(*paths, **kw)
    test.layer = layer

    return test


class RepositoryHelper:
    @property
    def repository(self):
        import zeit.cms.repository.interfaces

        with site(self.getRootFolder()):
            return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    @repository.setter
    def repository(self, value):
        self.__dict__['repository'] = value


class FunctionalTestCase(
    unittest.TestCase,
    gocept.testing.assertion.Ellipsis,
    gocept.testing.assertion.Exceptions,
    gocept.testing.assertion.String,
    RepositoryHelper,
):
    def getRootFolder(self):
        """Returns the Zope root folder."""
        return self.layer['zodbApp']

    def setUp(self):
        super().setUp()
        zope.component.hooks.setSite(self.getRootFolder())
        self.principal = create_interaction('zope.user')


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
    s.open('http://user:userpw@%s/++skin++vivi/@@test-setup-auth' % self['http_address'])
    # We don't really know how much time the browser needs until it's
    # satisfied, or how we could determine this.
    s.pause(1000)


original_setup = gocept.selenium.webdriver.WebdriverSeleneseLayer.setUp
gocept.selenium.webdriver.WebdriverSeleneseLayer.setUp = selenium_setup_authcache


def selenium_teardown_authcache(self):
    original_teardown(self)
    del self['http_auth_cache']


original_teardown = gocept.selenium.webdriver.WebdriverSeleneseLayer.tearDown
gocept.selenium.webdriver.WebdriverSeleneseLayer.tearDown = selenium_teardown_authcache


# XXX copy&paste to fix incorrect API usage (find_elements_by_xpath was removed)
def assertOrdered(self, locator1, locator2):
    if self._find(locator2).id not in {
        x.id for x in self.selenium.find_elements(By.XPATH, locator1 + '/following-sibling::*')
    }:
        raise self.failureException(
            'Element order did not match expected %r,%r' % (locator1, locator2)
        )


gocept.selenium.wd_selenese.Selenese.assertOrdered = assertOrdered


@pytest.mark.selenium()
class SeleniumTestCase(gocept.selenium.WebdriverSeleneseTestCase, FunctionalTestCase):
    skin = 'cms'
    log_errors = False
    log_errors_ignore = ()
    level = 2

    TIMEOUT = int(os.environ.get('ZEIT_SELENIUM_TIMEOUT', 10))

    window_width = 1100
    window_height = 600

    def setUp(self):
        super().setUp()
        self.layer['selenium'].setTimeout(self.TIMEOUT * 1000)

        if self.log_errors:
            error_log = zope.component.getUtility(zope.error.interfaces.IErrorReportingUtility)
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
        self.execute('window.localStorage.clear()')

    def tearDown(self):
        super().tearDown()
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
            'http://%s%s/++skin++%s%s' % (auth, self.selenium.server, self.skin, path)
        )

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' % xml.sax.saxutils.quoteattr(label))

    js_globals = """\
        var document = window.document;
        var zeit = window.zeit;
    """

    def execute(self, text):
        return self.selenium.selenium.execute_script(self.js_globals + text)

    def eval(self, text):
        return self.execute('return ' + text)

    def wait_for_condition(self, text):
        self.selenium.waitForCondition(
            self.js_globals
            + """\
        return Boolean(%s);
        """
            % text
        )

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
    browser.follow_redirects = False
    try:
        browser.getLink(*args, **kwargs).click()
        print((browser.headers['Status']))
        print((browser.headers['Location']))
    finally:
        browser.follow_redirects = True


def set_site(site=None):
    """Encapsulation of the getSite/setSite-dance, with doctest support."""
    globs = sys._getframe(1).f_locals
    if site is None:
        site = globs['getRootFolder']()
    zope.component.hooks.setSite(site)


# XXX use zope.publisher.testing for the following two
def create_interaction(name='zope.user'):
    principal = zope.security.testing.Principal(
        name, groups=['zope.Authenticated'], description='test@example.com'
    )
    request = zope.publisher.browser.TestRequest()
    request.setPrincipal(principal)
    zope.security.management.newInteraction(request)
    return principal


@contextlib.contextmanager
def interaction(principal_id='zope.user'):
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
    old_site = zope.component.hooks.getSite()
    zope.component.hooks.setSite(root)
    yield
    zope.component.hooks.setSite(old_site)


@zope.interface.implementer(zope.i18n.interfaces.IGlobalMessageCatalog)
class TestCatalog:
    language = 'tt'
    messages = {}

    def queryMessage(self, msgid, default=None):
        return self.messages.get(msgid, default)

    getMessage = queryMessage

    def getIdentifier(self):
        return 'test'

    def reload(self):
        pass


class NoopDatamanager:
    """Datamanager which does nothing."""

    def abort(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_begin(self, trans):
        pass

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return 'anything'


class CommitExceptionDataManager(NoopDatamanager):
    """DataManager which raises an exception in tpc_vote."""

    def __init__(self, error):
        self.error = error

    def tpc_vote(self, trans):
        raise self.error


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


class Browser(zope.testbrowser.browser.Browser):
    follow_redirects = True
    xml_strict = False

    def __init__(self, wsgi_app):
        super().__init__(wsgi_app=wsgi_app)

    def open(self, url, *args, **kw):
        if url.startswith('/'):
            url = 'http://localhost/++skin++vivi' + url
        return super().open(url, *args, **kw)

    def login(self, username, password):
        auth = base64.b64encode(('%s:%s' % (username, password)).encode('utf-8')).decode('ascii')
        self.addHeader('Authorization', 'Basic %s' % auth)

    def reload(self):
        # Don't know what the superclass is doing here, exactly, but it's not
        # helpful at all, so we reimplement it in a hopefully more sane way.
        if self._response is None:
            raise zope.testbrowser.browser.BrowserStateError('No URL has yet been .open()ed')
        self.open(self.url)

    def _processRequest(self, url, make_request):
        self._document = None
        transaction.commit()
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(None)
        old_interaction = zope.security.management.queryInteraction()
        zope.security.management.endInteraction()
        try:
            # No super call, since we had to copy&paste the whole method.
            self._do_processRequest(url, make_request)
        finally:
            zope.component.hooks.setSite(old_site)
            if old_interaction:
                zope.security.management.thread_local.interaction = old_interaction

    # copy&paste from superclass _processRequest to plug in `follow_redirects`
    def _do_processRequest(self, url, make_request):
        with self._preparedRequest(url) as reqargs:
            self._history.add(self._response)
            resp = make_request(reqargs)
            if self.follow_redirects:
                remaining_redirects = 100  # infinite loops protection
                while remaining_redirects and resp.status_int in zope.testbrowser.browser.REDIRECTS:
                    remaining_redirects -= 1
                    url = urljoin(url, resp.headers['location'])
                    with self._preparedRequest(url) as reqargs:
                        resp = self.testapp.get(url, **reqargs)
                assert remaining_redirects > 0, 'redirect chain looks infinite'
            self._setResponse(resp)
            self._checkStatus()

    HTML_PARSER = lxml.html.HTMLParser(encoding='UTF-8')
    _document = None

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self._document is not None:
            return self._document
        if self.contents is None:
            return None
        if self.xml_strict:
            self._document = lxml.etree.fromstring(self.contents)
        else:
            self._document = lxml.html.document_fromstring(self.contents, parser=self.HTML_PARSER)
        return self._document

    def xpath(self, selector, **kw):
        """Return a list of lxml.HTMLElement instances that match a given
        XPath selector.
        """
        if self.document is None:
            return None
        return self.document.xpath(selector, **kw)

    def cssselect(self, selector, **kw):
        return self.xpath(lxml.cssselect.CSSSelector(selector).path, **kw)


# Allow webtest to handle file download result iterators
webtest.lint.isinstance = zope.security.proxy.isinstance


class BrowserTestCase(FunctionalTestCase, BrowserAssertions):
    login_as = ('user', 'userpw')

    def setUp(self):
        super().setUp()
        self.browser = Browser(self.layer['wsgi_app'])
        if isinstance(self.login_as, str):  # BBB:
            self.login_as = self.login_as.split(':')
        self.browser.login(*self.login_as)


# These ugly names are due to two reasons:
# 1. zeit.cms.testing contains both general test mechanics *and*
#    specific test infrastructure/layers for zeit.cms itself
# 2. pytest does not allow for subclassing a TestCase and changing its layer
#    (for the same reason as copy_inherited_functions above).


class ZeitCmsTestCase(FunctionalTestCase):
    layer = ZOPE_LAYER


class ZeitCmsBrowserTestCase(BrowserTestCase):
    layer = WSGI_LAYER


class JSLintTestCase(gocept.jslint.TestCase):
    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/true')

    options = {
        'esversion': '6',
        'evil': True,
        'eqnull': True,
        'multistr': True,
        'sub': True,
        'undef': True,
        'browser': True,
        'jquery': True,
        'devel': True,
    }
    predefined = (
        'zeit',
        'gocept',
        'application_url',
        'context_url',
        'DOMParser',
        'escape',
        'unescape',
        'jsontemplate',
        'MochiKit',
        '$$',
        'forEach',
        'filter',
        'map',
        'extend',
        'bind',
        'log',
        'repr',
        'logger',
        'logDebug',
        'logError',  # XXX
        'DIV',
        'A',
        'UL',
        'LI',
        'INPUT',
        'IMG',
        'SELECT',
        'OPTION',
        'BUTTON',
        'SPAN',
        'LABEL',
        'isNull',
        'isUndefined',
        'isUndefinedOrNull',
        'Uri',
        '_',  # js.underscore
    )

    ignore = (
        'Functions declared within loops',
        "Expected an identifier and instead saw 'import'",
        "Use '===' to compare with",
        "Use '!==' to compare with",
        'Missing radix parameter',
        'Misleading line break',
        'Expected an assignment or function call and instead' ' saw an expression',
    )

    def _write_config_file(self):
        """Copy&paste from baseclass, so we can use non-boolean options."""
        settings = self.options.copy()
        predefined = settings['predef'] = []
        for name in self.predefined:
            predefined.append(name)

        handle, filename = tempfile.mkstemp()
        output = open(filename, 'w')
        json.dump(settings, output)
        output.close()

        return filename


def xmltotext(xml):
    xml = copy.deepcopy(xml)
    lxml.etree.indent(xml)
    return lxml.etree.tostring(xml, encoding=str)
