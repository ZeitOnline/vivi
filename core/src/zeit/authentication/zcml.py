from zope.pluggableauth.factories import PrincipalInfo
import zope.interface
import zope.pluggableauth.interfaces
import zope.principalregistry.principalregistry


@zope.interface.implementer(zope.pluggableauth.interfaces.IAuthenticatorPlugin)
class PrincipalRegistryAuthenticator:
    """Connects PAU to zope.principalregistry."""

    registry = zope.principalregistry.principalregistry.principalRegistry

    def authenticateCredentials(self, credentials):
        if credentials is None:
            return None

        try:
            user = self.registry.getPrincipalByLogin(credentials['login'])
        except KeyError:
            user = None
        if user is None:
            return None
        if not user.validate(credentials['password']):
            return None

        return self._principal_info(user)

    def principalInfo(self, id):
        try:
            user = self.registry.getPrincipal(id)
        except zope.authentication.interfaces.PrincipalLookupError:
            return None
        if user is None:
            return None
        return self._principal_info(user)

    def _principal_info(self, user):
        return PrincipalInfo(user.id, user.getLogin(), user.title, '')
