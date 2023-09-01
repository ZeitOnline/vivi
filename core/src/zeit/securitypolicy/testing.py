from zeit.cms.testing import FunctionalTestCase
import plone.testing
import urllib.parse
import zeit.brightcove.testing
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.retresco.testing
import zope.component
import zope.component.hooks


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    def testSetUp(self):
        # Tweak pushGlobalRegistry so the registry does not have any bases,
        # otherwise zope.authentication.principal infloops because
        # zope.component.queryNextUtility() always finds a base and never stops
        base = self['zcaRegistry']
        registry = zope.component.globalregistry.BaseGlobalComponents(__name__)
        registry.adapters.__bases__ = (base.adapters,)
        registry.utilities.__bases__ = (base.utilities,)
        plone.testing.zca.pushGlobalRegistry(registry)
        self.registry = registry

    def testTearDown(self):
        self.registry.__bases__ = (self['zcaRegistry'],)
        plone.testing.zca.popGlobalRegistry()


ZCML_LAYER = ZCMLLayer(bases=(
    zeit.brightcove.testing.CONFIG_LAYER,
    zeit.retresco.testing.CONFIG_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(
    ZCML_LAYER, zeit.retresco.testing.TMS_MOCK_LAYER))


class SecurityPolicyLayer(plone.testing.Layer):

    defaultBases = (ZOPE_LAYER,)

    def testSetUp(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        prop = connector._get_properties(
            'http://xml.zeit.de/online/2007/01/Somalia')
        prop[zeit.cms.tagging.testing.KEYWORD_PROPERTY] = 'testtag'


LAYER = SecurityPolicyLayer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


def make_xls_test(*args):
    # Since pytest picks up all descendants of unittest.TestCase, we must mix
    # that in here instead of directly having XLSSheetCase inherit from
    # FunctionalTestCaseCommon.
    case = type(
        'SecurityPolicyXLSSheetCase',
        (SecurityPolicyXLSSheetCase, FunctionalTestCase), {})
    return case(*args)


class SecurityPolicyXLSSheetCase:

    layer = WSGI_LAYER

    def __init__(self, username, cases, description):
        super().__init__()
        self.username = username
        self.cases = cases
        self.description = description

    def setUp(self):
        super().setUp()
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        self.browser.raiseHttpErrors = False
        if self.username != 'anonymous':
            password = self.username + 'pw'
            self.browser.login(self.username, password)

    def runTest(self):
        for skin, path, form, expected in self.cases:
            if skin.strip() == 'python:':
                test = self  # noqa needed by the eval() call below
                site = zope.component.hooks.getSite()
                zope.component.hooks.setSite(self.getRootFolder())
                try:
                    # XXX pass variables in explicitly
                    eval(path)
                finally:
                    zope.component.hooks.setSite(site)
                continue
            path_with_skin = 'http://localhost/++skin++%s%s' % (skin, path)
            path_with_skin = path_with_skin % {'username': self.username}

            if form:
                self.browser.post(
                    path_with_skin,
                    # XXX pass variables in explicitly
                    urllib.parse.urlencode(eval(form)))
            else:
                self.browser.open(path_with_skin)

            status, msg = self.browser.headers['Status'].split(' ', 1)
            self.assertEqual(
                (int(status) < 400), expected,
                '%s: %s (expected <400: %s)\n%s' % (
                    path, status, bool(expected), self.browser.contents))

    def __str__(self):
        return '%s (%s.%s)' % (
            self.description,
            self.__class__.__module__, self.__class__.__name__)

    @property
    def connector(self):  # for eval()
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)
