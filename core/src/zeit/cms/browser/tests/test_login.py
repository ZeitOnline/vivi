from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
import gocept.testing.assertion
import plone.testing
import transaction
import zeit.cms.generation.install
import zeit.cms.testing
import zope.authentication.interfaces
import zope.component
import zope.pluggableauth.authentication
import zope.pluggableauth.interfaces


class LoginFormLayer(plone.testing.Layer):

    defaultBases = (zeit.cms.testing.ZCML_LAYER,)

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


class LoginFormTest(zeit.cms.testing.BrowserTestCase,
                    gocept.testing.assertion.String):

    layer = LOGINFORM_LAYER

    def setUp(self):
        super(LoginFormTest, self).setUp()
        self.browser = zeit.cms.testing.Browser()

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
