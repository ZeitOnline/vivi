from zope.authentication.interfaces import IUnauthenticatedPrincipal
import jwt
import time
import webob.cookies
import zeit.cms.browser.resources
import zope.app.appsetup.product
import zope.authentication.interfaces
import zope.traversing.browser


class Login:
    """The actual login (authentication and remembering) is performed behind
    the scenes by the IAuthentication utility, registered by zeit.ldap.
    (The view name `loginForm.html` and the `camefrom` parameter are part of
    that protocol.)
    """

    def __call__(self):
        zeit.cms.browser.resources.login_css.need()
        if not self.authenticated:
            # Render template with error message
            result = super().__call__()
            return result
        if self.camefrom:
            return self.request.response.redirect(self.camefrom)
        return self.request.response.redirect(
            zope.traversing.browser.absoluteURL(self.context, self.request))

    @property
    def camefrom(self):
        return self.request.get('camefrom')

    @property
    def authenticated(self):
        unauthenticated = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)
        return not unauthenticated

    @property
    def submitted(self):
        return self.request.method == 'POST'

    @property
    def environment(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        return config['environment']


class Logout:

    def __call__(self):
        logged_out = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)

        if not logged_out:
            auth = zope.component.getUtility(
                zope.authentication.interfaces.IAuthentication)
            zope.authentication.interfaces.ILogout(auth).logout(self.request)
            self._delete_sso_cookies()

    def _delete_sso_cookies(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        prefix = config.get('sso-cookie-name-prefix')
        if prefix is None:
            return
        for cookie in self.request.cookies:
            if cookie.startswith(prefix):
                for key, value in set_cookie_headers(cookie, None):
                    self.request.response.setHeader(key, value)


class SSOLogin:
    """Provide a vivi-powered, cookie-based single-sign-on functionality.

    This is the same basic concept as the "big SSO", meine.zeit.de:

    * The client application checks for SSO cookie, if not present, it
      redirects to this view.
    * We authenticate the user with the usual vivi mechanism (login form). If
      successful (or if they were already logged into vivi), we set the SSO
      cookie and redirect back to the url passed in by the client via the `url`
      query parameter.
    * The client can request the permission that the user must have via the
      `permission` query parameter (defaults to zope.View, which is the "is a
      logged in user" permission). The SSO cookie is named like the permission,
      e.g. `vivi_sso_ticket_zope.View`, and set for all of zeit.de. It expires
      on browser close, so there is no need for any explicit logout.
    """

    def __call__(self):
        permission = self.request.form.get('permission', 'zope.View')
        if not self.request.interaction.checkPermission(
                permission, self.context):
            raise zope.security.interfaces.Unauthorized(permission)
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        principal = self.request.principal
        with open(config['sso-private-key-file']) as f:
            private_key = f.read()
        headers = set_cookie_headers(
            config['sso-cookie-name-prefix'] + permission,
            jwt.encode({
                'id': principal.id,
                'name': principal.title,
                'email': principal.description,
                # XXX Once TMS haproxy learns to validate JWT, use a single
                # cookie with all permissions (or probably roles) instead.
                'permissions': [permission],
                'exp': int(time.time()) + int(config['sso-expiration']),
            }, private_key, config['sso-algorithm']).decode('ascii'))
        for key, value in headers:
            self.request.response.setHeader(key, value)
        url = self.request.form.get('url', zope.traversing.browser.absoluteURL(
            self.context, self.request))
        return self.request.response.redirect(url, trusted=True)


def set_cookie_headers(name, value):
    # Inspired by zeit.web.member.security._set_cookie_headers()
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    cookie_helper = webob.cookies.CookieProfile(
        name, serializer=SIMPLE_SERIALIZER)
    if config['sso-cookie-domain']:
        domains = [config['sso-cookie-domain']]
    else:
        # Applies only in tests and localhost environment; since at least
        # zope.testbrowser does not understand "Domain=localhost", sigh.
        domains = [None]
    return cookie_helper.get_headers(
        value, domains=domains, max_age=EXPIRE_ON_BROWSER_CLOSE)


class SimpleSerializer:
    """Copied from pyramid.authentication._SimpleSerializer."""

    def loads(self, bstruct):
        if isinstance(bstruct, str):
            return bstruct.encode('latin-1')
        return str(bstruct)

    def dumps(self, appstruct):
        if isinstance(appstruct, str):
            return appstruct.encode('latin-1')
        return appstruct


SIMPLE_SERIALIZER = SimpleSerializer()
EXPIRE_ON_BROWSER_CLOSE = None
