import zope.authentication.interfaces
import zope.component
import zope.component.hooks
import zope.interface
import zope.pluggableauth.authentication
import zope.pluggableauth.plugins.httpplugins
import zope.pluggableauth.plugins.session
import zope.session.interfaces
import zope.traversing.browser

import zeit.cms.config


@zope.interface.implementer(zope.authentication.interfaces.IAuthentication)
def from_product_config():
    conf = zeit.cms.config.package('zeit.authentication')
    pau = zope.pluggableauth.authentication.PluggableAuthentication()
    pau.authenticatorPlugins = conf['authenticator-plugins'].split(',')
    pau.credentialsPlugins = conf['credentials-plugins'].split(',')
    return pau


class BasicAuthCredentials(zope.pluggableauth.plugins.httpplugins.HTTPBasicAuthCredentialsPlugin):
    """We only support basic auth on non-public ingress endpoints, e.g. for
    xmlrpc requests and administrative access.
    """

    header_name = 'X-Zope-Basicauth'

    def _enabled(self, request):
        return request.headers.get(self.header_name, '') != 'disabled'

    def extractCredentials(self, request):
        if not self._enabled(request):
            return None
        return super().extractCredentials(request)

    def challenge(self, request):
        if not self._enabled(request):
            return False
        return super().challenge(request)


class SessionCredentials(zope.pluggableauth.plugins.session.SessionCredentialsPlugin):
    """Make PAU work as a non-persistent utility.

    The upstream assumption is to be persistent, i.e. at least traversal to
    the root folder will have already happened, so any other persistent
    utilities (like the zope.session ClientIdManager) are available.
    We don't need/want the PAU to be persistent, so we register it with the
    global ZCA registry. This means, it can and will be used before any
    traversal happens (e.g. by ZCML to access principals for grant operations).
    Since actual authentication only makes sense after at least traversing to
    the root folder, we can simply ignore attempts that happen before that.
    """

    def extractCredentials(self, request):
        # The "proper" way to check would be `ISession(request)`, but since
        # this is going to be called on every request before traversal starts,
        # let's make it as cheap-to-fail as possible.
        if zope.component.queryUtility(zope.session.interfaces.IClientIdManager) is None:
            return None
        return super().extractCredentials(request)

    def logout(self, request):
        # Strictly speaking, things like redirecting the browser are the job of
        # the logout view. But since we need different treatments for session
        # and oidc, it's probably fair to put them in their credentials plugin.
        if not super().logout(request):
            return False
        home = zope.traversing.browser.absoluteURL(zope.component.hooks.getSite(), request)
        request.response.redirect(home)
        return True
