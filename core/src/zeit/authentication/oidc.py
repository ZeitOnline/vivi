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
    name_header = 'X-OIDC-User'
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
            'name': request.headers.get(  # PEP-3333 is weird
                self.name_header, ''
            )
            .encode('latin-1')
            .decode('utf-8'),
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
        'name_header': 'oidc-header-name',
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
        return PrincipalInfo(email, email, credentials['name'], email)

    @CONFIG_CACHE.cache_on_arguments()
    def principalInfo(self, id):
        # `id` is the email address
        id = id.lower()
        ad = zope.component.getUtility(zeit.authentication.azure.IActiveDirectory)
        user = ad.get_user(id)
        if not user:
            return None
        return PrincipalInfo(id, id, user['displayName'], id)

    schema = IAzureSearchSchema

    def search(self, query, start=None, batch_size=None):
        ad = zope.component.getUtility(zeit.authentication.azure.IActiveDirectory)
        result = [x['userPrincipalName'].lower() for x in ad.search_users(query['query'])]
        if start is None:
            start = 0
        if batch_size is None:
            batch_size = len(result)
        return result[start : start + batch_size]
