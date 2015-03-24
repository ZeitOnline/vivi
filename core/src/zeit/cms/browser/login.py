from zope.authentication.interfaces import IUnauthenticatedPrincipal
import zeit.cms.browser.resources
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


class Logout(object):

    def __call__(self):
        logged_out = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)

        if not logged_out:
            auth = zope.component.getUtility(
                zope.authentication.interfaces.IAuthentication)
            zope.authentication.interfaces.ILogout(auth).logout(self.request)

        return self.request.response.redirect(
            zope.traversing.browser.absoluteURL(self.context, self.request))
