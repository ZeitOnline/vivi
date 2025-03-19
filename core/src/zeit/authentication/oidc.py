from zope.pluggableauth.factories import PrincipalInfo
from zope.publisher.interfaces.http import IHTTPRequest
import zope.component
import zope.interface
import zope.pluggableauth.interfaces
import zope.schema

from zeit.cms.interfaces import CONFIG_CACHE
import zeit.authentication.azure
import zeit.cms.config


@zope.interface.implementer(zope.pluggableauth.interfaces.ICredentialsPlugin)
class OIDCHeaderCredentials:
    email_header = 'X-OIDC-Email'
    logout_url = '/oauth2/sign_in'  # clears oidc cookies and prompts to login

    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy(request):
            return None
        if self.email_header not in request.headers:
            return None
        return {
            'oidc': True,  # Use a marker interface instead?
            'login': request.headers[self.email_header],
            'password': '',  # Implicit zope.pluggableauth protocol
        }

    def challenge(self, request):
        # Challenging is already handled by nginx+oauth-proxy.
        return False

    def logout(self, request):
        home = zope.traversing.browser.absoluteURL(zope.component.hooks.getSite(), request)
        request.response.redirect(home + self.logout_url)
        return True


@zope.interface.implementer(zope.pluggableauth.interfaces.ICredentialsPlugin)
def from_product_config():
    config = zeit.cms.config.package('zeit.authentication')
    plugin = OIDCHeaderCredentials()
    settings = {
        'email_header': 'oidc-header-email',
        'logout_url': 'oidc-logout-url',
    }
    for prop, key in settings.items():
        if key in config:
            setattr(plugin, prop, config[key])
    return plugin


class IAzureSearchSchema(zope.interface.Interface):
    query = zope.schema.TextLine(title='Azure AD Name (substring)', required=False)


@zope.interface.implementer(
    zope.pluggableauth.interfaces.IAuthenticatorPlugin,
    zope.pluggableauth.interfaces.IQueriableAuthenticator,
    zope.pluggableauth.interfaces.IQuerySchemaSearch,
)
class AzureADAuthenticator:
    def authenticateCredentials(self, credentials):
        if credentials is None:
            return None
        if 'oidc' not in credentials:  # See OIDCHeaderCredentials
            return None
        email = credentials['login'].lower()
        return PrincipalInfo(email, email, email, email)

    @CONFIG_CACHE.cache_on_arguments()
    def principalInfo(self, id):
        # We differentiate multiple AuthenticatorPlugins by their ID syntax.
        # AD users use the email address from the oidc ID token
        # (see also https://docs.zeit.de/ops/k8s/cluster-infra/oidc/#funote-externe-accounts)
        # while ZCML users use IDs like `zope.name` or `system.name`.
        if '@' not in id:
            return None
        id = id.lower()
        return PrincipalInfo(id, id, id, id)

    schema = IAzureSearchSchema

    def search(self, query, start=None, batch_size=None):
        ad = zope.component.getUtility(zeit.authentication.azure.IActiveDirectory)
        result = [x['userPrincipalName'].lower() for x in ad.search_users(query['query'])]
        if start is None:
            start = 0
        if batch_size is None:
            batch_size = len(result)
        return result[start : start + batch_size]
