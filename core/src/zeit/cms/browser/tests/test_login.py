from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
import json
import plone.testing
import transaction
import urllib
import urllib2
import zeit.cms.generation.install
import zeit.cms.testing
import zope.authentication.interfaces
import zope.component
import zope.pluggableauth.authentication
import zope.pluggableauth.interfaces
import zope.securitypolicy.interfaces


class LoginFormLayer(plone.testing.Layer):

    defaultBases = (zeit.cms.testing.WSGI_LAYER,)

    def setUp(self):
        root = self['functional_setup'].getRootFolder()
        self['principalfolder'] = PrincipalFolder('principal.')
        root['principals'] = self['principalfolder']
        self['principalfolder']['user'] = InternalPrincipal(
            'user', 'userpw', u'Testuser')

        with zeit.cms.testing.site(root):
            site_manager = zope.component.getSiteManager()

            site_manager.registerUtility(
                root['principals'],
                zope.pluggableauth.interfaces.IAuthenticatorPlugin,
                name='principalfolder')

            auth = zeit.cms.generation.install.installLocalUtility(
                site_manager,
                zope.pluggableauth.authentication.PluggableAuthentication,
                'authentication',
                zope.authentication.interfaces.IAuthentication)
            auth.authenticatorPlugins = ('principalfolder',)
            auth.credentialsPlugins = (
                'No Challenge if Authenticated',
                'Session Credentials')
            transaction.commit()

    def tearDown(self):
        del self['principalfolder']

LOGINFORM_LAYER = LoginFormLayer()


class LoginFormTest(zeit.cms.testing.BrowserTestCase):

    layer = LOGINFORM_LAYER

    def setUp(self):
        super(LoginFormTest, self).setUp()
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def test_unauthenticated_redirects_to_loginform(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        self.assertIn('@@loginForm.html', b.url)

    def test_correct_credentials_redirects_to_camefrom(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        b.getControl('Username').value = 'user'
        b.getControl('Password').value = 'userpw'
        b.getControl('Log in').click()
        self.assertEndsWith('/repository', b.url)

    def test_invalid_credentials_display_error(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        b.getControl('Log in').click()
        self.assertEllipsis('...Login failed...', b.contents)
        # Ensure the message is not always displayed.
        b.open('http://localhost/++skin++vivi/repository')
        self.assertNotIn('Login failed', b.contents)


class SSOTest(zeit.cms.testing.BrowserTestCase):

    layer = LOGINFORM_LAYER

    def setUp(self):
        super(SSOTest, self).setUp()
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def login(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        b.getControl('Username').value = 'user'
        b.getControl('Password').value = 'userpw'
        b.getControl('Log in').click()

    def test_unauthenticated_redirects_to_loginform(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/sso-login')
        self.assertIn('loginForm.html', b.url)

    def test_have_permission_redirects_to_url(self):
        self.login()
        b = self.browser
        b.follow_redirects = False
        b.open('http://localhost/++skin++vivi/sso-login'
               '?url=http://example.com/path')
        self.assertEqual('http://example.com/path', b.headers.get('location'))

    def test_have_permission_sets_cookie(self):
        self.login()
        b = self.browser
        b.open('http://localhost/++skin++vivi/sso-login')
        # See zeit.cms.repository.browser.entrypage, which is unused in
        # production, but still active in tests.
        self.assertEqual(
            'http://localhost/++skin++vivi/repository/online/2008/26', b.url)
        cookie = b.cookies.getinfo('my_sso_zope.View')
        self.assertEqual(None, cookie['expires'])
        data = json.loads(cookie['value'].decode('base64'))
        self.assertEqual('principal.user', data['id'])

    def test_url_parameter_redirects_all_the_way_back_after_login(self):
        b = self.browser
        target = 'http://localhost/++skin++vivi/repository/2016'
        b.open('http://localhost/++skin++vivi/sso-login?url=' +
               urllib.quote_plus(target))
        b.getControl('Username').value = 'user'
        b.getControl('Password').value = 'userpw'
        b.getControl('Log in').click()
        self.assertEqual(target, b.url)

    def test_required_permission_produces_named_cookie(self):
        perms = zope.securitypolicy.interfaces.IPrincipalPermissionManager(
            self.repository.__parent__)
        perms.grantPermissionToPrincipal(
            'zeit.cms.admin.View', 'principal.user')
        self.login()
        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/sso-login?permission=zeit.cms.admin.View')
        cookie = b.cookies.getinfo('my_sso_zeit.cms.admin.View')
        data = json.loads(cookie['value'].decode('base64'))
        self.assertEqual('principal.user', data['id'])

    def test_user_without_required_permission_shows_unauthorized(self):
        self.login()
        b = self.browser
        with self.assertRaises(urllib2.HTTPError) as info:
            b.open('http://localhost/++skin++vivi'
                   '/sso-login?permission=zeit.cms.admin.View')
            self.assertEqual(403, info.exception.status)

    def test_logout_deletes_sso_cookies(self):
        self.login()
        b = self.browser
        b.open('http://localhost/++skin++vivi/sso-login')
        self.assertIn('my_sso_zope.View', b.cookies)
        b.open('http://localhost/++skin++vivi/logout.html')
        self.assertNotIn('my_sso_zope.View', b.cookies)
