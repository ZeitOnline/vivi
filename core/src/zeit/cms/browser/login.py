from zope.authentication.interfaces import IUnauthenticatedPrincipal
import base64
import json
import six
import webob.cookies
import zeit.cms.browser.resources
import zope.app.appsetup.product
import zope.authentication.interfaces
import zope.traversing.browser


class Login(object):
    """The actual login (authentication and remembering) is performed behind
    the scenes by the IAuthentication utility, registered by zeit.ldap.
    (The view name `loginForm.html` and the `camefrom` parameter are part of
    that protocol.)
    """

    def __call__(self):
        zeit.cms.browser.resources.login_css.need()
        if not self.authenticated:
            # Render template with error message
            result = super(Login, self).__call__()
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


class Logout(object):

    def __call__(self):
        logged_out = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)

        if not logged_out:
            auth = zope.component.getUtility(
                zope.authentication.interfaces.IAuthentication)
            zope.authentication.interfaces.ILogout(auth).logout(self.request)
            self._delete_sso_cookies()

        return self.request.response.redirect(
            zope.traversing.browser.absoluteURL(self.context, self.request))

    def _delete_sso_cookies(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        for cookie in self.request.cookies:
            if cookie.startswith(config['sso-cookie-name-prefix']):
                for key, value in set_cookie_headers(cookie, None):
                    self.request.response.setHeader(key, value)


class SSOLogin(object):
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
    * Note that the cookie currently does not contain any meaningful value, so
      clients need only be concerned with its presence. (We don't need to worry
      about spoofing, since this is strictly a company-interal mechanism.)
    """

    def __call__(self):
        permission = self.request.form.get('permission', 'zope.View')
        if not self.request.interaction.checkPermission(
                permission, self.context):
            raise zope.security.interfaces.Unauthorized(permission)
        # XXX We'd want to use a signed JWT as the value, just like
        # zeit.accounts does, but our currently only client (haproxy of TMS)
        # cannot evaluate that, so there's not much point right now.
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        principal = self.request.principal
        headers = set_cookie_headers(
            config['sso-cookie-name-prefix'] + permission,
            base64.b64encode(json.dumps({
                'id': principal.id, 'name': principal.title,
                'email': principal.description}
            ).encode('utf-8')).decode('ascii'))
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
        value, domains=domains, max_age=EXPIRE_ON_BROSWER_CLOSE)


class SimpleSerializer(object):
    """Copied from pyramid.authentication._SimpleSerializer."""

    def loads(self, bstruct):
        if isinstance(bstruct, six.text_type):
            return bstruct.encode('latin-1')
        return str(bstruct)

    def dumps(self, appstruct):
        if isinstance(appstruct, six.text_type):
            return appstruct.encode('latin-1')
        return appstruct


SIMPLE_SERIALIZER = SimpleSerializer()
EXPIRE_ON_BROSWER_CLOSE = None
