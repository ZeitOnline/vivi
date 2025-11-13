import contextlib
import copy
import importlib.resources
import os.path
import sys
import unittest

import gocept.testing.assertion
import opentelemetry.util.http
import plone.testing.zca
import plone.testing.zodb
import transaction
import ZODB
import ZODB.DemoStorage
import zope.app.publication.zopepublication
import zope.app.wsgi
import zope.component
import zope.component.hooks
import zope.processlifetime
import zope.security.testing

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.wsgi

from .celery import CELERY_EAGER_LAYER
from .layer import LOGGING_LAYER, Layer
from .mock import MOCK_RESET_LAYER


class FunctionalTestCase(
    unittest.TestCase,
    gocept.testing.assertion.Ellipsis,
    gocept.testing.assertion.Exceptions,
    gocept.testing.assertion.String,
):
    def getRootFolder(self):
        """Returns the Zope root folder."""
        return self.layer['zodbApp']

    @property
    def repository(self):
        with site(self.getRootFolder()):
            return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    def setUp(self):
        super().setUp()
        zope.component.hooks.setSite(self.getRootFolder())
        self.principal = create_interaction('zope.user')


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


class ProductConfigLayer(Layer):
    DELETE = object()

    def __init__(self, config, package=None, patches=None, bases=None):
        super().__init__(bases)
        if not package:
            package = '.'.join(self.__module__.split('.')[:-1])
        self.package = package
        self.config = config
        self.patches = patches or {}

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


class ZCMLLayer(Layer):
    defaultBases = (LOGGING_LAYER,)

    def __init__(
        self,
        bases=(),
        config_file='ftesting.zcml',
        features=('zeit.connector.mock',),
    ):
        from .sql import SQL_CONFIG_LAYER  # break circular import

        if not isinstance(bases, tuple):
            bases = (bases,)
        if any(x.startswith('zeit.connector.sql') for x in features):
            bases += (SQL_CONFIG_LAYER,)

        super().__init__(bases=self.defaultBases + bases)
        package, _ = self.__module__.rsplit('.', 1)
        if not config_file.startswith('/'):
            config_file = str((importlib.resources.files(package) / config_file))
        self.config_file = config_file
        self.features = features

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


class AdditionalZCMLLayer(Layer):
    """Requires a ZCMLLayer instance in the layer hierarchy above it."""

    def __init__(self, package=None, config_file='configure.zcml', bases=()):
        super().__init__(self.defaultBases + bases)
        if package is None:
            package, _ = self.__module__.rsplit('.', 1)
        if not config_file.startswith('/'):
            config_file = str((importlib.resources.files(package) / config_file))
        self.config_file = config_file

    def setUp(self):
        self['zcaRegistryAdd'] = plone.testing.zca.pushGlobalRegistry()
        zope.configuration.xmlconfig.include(self['zcaContext'], file=self.config_file)
        self['zcaContext'].execute_actions()

    def tearDown(self):
        plone.testing.zca.popGlobalRegistry()
        del self['zcaRegistryAdd']


class ZODBLayer(Layer):
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


class ZopeLayer(Layer):
    defaultBases = (CELERY_EAGER_LAYER, MOCK_RESET_LAYER)

    def __init__(self, bases=()):
        if not isinstance(bases, tuple):
            bases = (bases,)
        super().__init__(
            # This is a bit kludgy. We need an individual ZODB layer per ZCML
            # file (so e.g. different install generations are isolated), but
            # we don't really want to have to create one per package.
            self.defaultBases + bases + (ZODBLayer(),),
        )

    def setUp(self):
        zope.event.notify(zope.processlifetime.DatabaseOpened(self['zodbDB-layer']))
        transaction.commit()
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


def IsolatedZopeLayer(bases, create_fixture=None, create_testcontent=True):
    from .sql import SQLIsolationSavepointLayer  # break circular import

    return SQLIsolationSavepointLayer(ZopeLayer(bases), create_fixture, create_testcontent)


class WSGILayer(Layer):
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
