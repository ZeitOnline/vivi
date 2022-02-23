from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
import jwt
import pkg_resources
import plone.testing
import six.moves.urllib.error
import six.moves.urllib.parse
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
        with self['rootFolder'](self['zodbDB-layer']) as root:
            with zeit.cms.testing.site(root):
                self['principalfolder'] = PrincipalFolder('principal.')
                root['principals'] = self['principalfolder']
                self['principalfolder']['user'] = InternalPrincipal(
                    'user', 'userpw', u'Testuser')

                site_manager = zope.component.getSiteManager(root)
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

    def tearDown(self):
        # We cannot just have ZODB_LAYER throw away a DB stack entry, since if
        # you set a resource from further above in the layer hierarchy it's not
        # available to lower levels. So we'd have to come up with some clever
        # inheritance scheme and probably create 5 new layer instances to
        # support this -- it's way easier to just clean up explicitly.
        with self['rootFolder'](self['zodbDB-layer']) as root:
            site_manager = zope.component.getSiteManager(root)
            site_manager.unregisterUtility(
                site_manager['authentication'],
                zope.authentication.interfaces.IAuthentication)
            del site_manager['authentication']
            del root['principals']
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

    def jwt_decode(self, value):
        return jwt.decode(
            value.encode('ascii'),
            pkg_resources.resource_string('zeit.cms.tests', 'sso-public.pem'),
            algorithms='RS256')

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
        data = self.jwt_decode(cookie['value'])
        self.assertEqual('principal.user', data['id'])

    def test_url_parameter_redirects_all_the_way_back_after_login(self):
        b = self.browser
        target = 'http://localhost/++skin++vivi/repository/2016'
        b.open('http://localhost/++skin++vivi/sso-login?url=' +
               six.moves.urllib.parse.quote_plus(target))
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
        data = self.jwt_decode(cookie['value'])
        self.assertEqual('principal.user', data['id'])

    def test_user_without_required_permission_shows_unauthorized(self):
        self.login()
        b = self.browser
        with self.assertRaises(six.moves.urllib.error.HTTPError) as info:
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
