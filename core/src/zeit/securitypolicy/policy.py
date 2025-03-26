from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import (
    Allow,
    IPrincipalPermissionMap,
    IPrincipalRoleMap,
    IRolePermissionMap,
)
from zope.securitypolicy.zopepolicy import (
    SettingAsBoolean,
    globalPrincipalPermissionSetting,
    globalRolesForPermission,
    globalRolesForPrincipal,
)
import zope.component
import zope.securitypolicy.zopepolicy

from zeit.cms.repository.interfaces import IRepository, IRepositoryContent


class SecurityPolicy(zope.securitypolicy.zopepolicy.ZopeSecurityPolicy):
    def _get_parent(self, parent):
        """Patched to skip walking up the parent chain for IRepositoryContent;
        this saves us having to needlessly resolve every intermedediate folder.

        (Unfortunately, just using specialized IPrincipalPermissionMap etc.
        adapters is not enough to actually skip resolving __parent__, since the
        default value in most cases is `None`, which means "keep walking".)

        This could be an adapter instead of a plain function, but since
        we currently only need the single different usecase, it's not worth it.
        """
        if IRepositoryContent.providedBy(parent) and not IRepository.providedBy(parent):
            return zope.component.getUtility(IRepository)
        else:
            return getattr(parent, '__parent__', None)

    def cached_prinper(self, parent, principal, groups, permission):
        # Compute the permission, if any, for the principal.
        cache = self.cache(parent)
        try:
            cache_prin = cache.prin
        except AttributeError:
            cache_prin = cache.prin = {}

        cache_prin_per = cache_prin.get(principal)
        if not cache_prin_per:
            cache_prin_per = cache_prin[principal] = {}

        try:
            return cache_prin_per[permission]
        except KeyError:
            pass

        if parent is None:
            prinper = SettingAsBoolean[
                globalPrincipalPermissionSetting(permission, principal, None)
            ]
            cache_prin_per[permission] = prinper
            return prinper

        prinper = IPrincipalPermissionMap(parent, None)
        if prinper is not None:
            prinper = SettingAsBoolean[prinper.getSetting(permission, principal, None)]
            if prinper is not None:
                cache_prin_per[permission] = prinper
                return prinper

        parent = removeSecurityProxy(self._get_parent(parent))
        prinper = self.cached_prinper(parent, principal, groups, permission)
        cache_prin_per[permission] = prinper
        return prinper

    def cached_roles(self, parent, permission):
        cache = self.cache(parent)
        try:
            cache_roles = cache.roles
        except AttributeError:
            cache_roles = cache.roles = {}
        try:
            return cache_roles[permission]
        except KeyError:
            pass

        if parent is None:
            roles = {
                role: 1
                for (role, setting) in globalRolesForPermission(permission)
                if setting is Allow
            }
            cache_roles[permission] = roles
            return roles

        roles = self.cached_roles(removeSecurityProxy(self._get_parent(parent)), permission)
        roleper = IRolePermissionMap(parent, None)
        if roleper:
            roles = roles.copy()
            for role, setting in roleper.getRolesForPermission(permission):
                if setting is Allow:
                    roles[role] = 1
                elif role in roles:
                    del roles[role]

        cache_roles[permission] = roles
        return roles

    def cached_principal_roles(self, parent, principal):
        cache = self.cache(parent)
        try:
            cache_principal_roles = cache.principal_roles
        except AttributeError:
            cache_principal_roles = cache.principal_roles = {}
        try:
            return cache_principal_roles[principal]
        except KeyError:
            pass

        if parent is None:
            roles = {
                role: SettingAsBoolean[setting]
                for (role, setting) in globalRolesForPrincipal(principal)
            }
            roles['zope.Anonymous'] = True  # Everybody has Anonymous
            cache_principal_roles[principal] = roles
            return roles

        roles = self.cached_principal_roles(
            removeSecurityProxy(self._get_parent(parent)), principal
        )

        prinrole = IPrincipalRoleMap(parent, None)
        if prinrole:
            roles = roles.copy()
            for role, setting in prinrole.getRolesForPrincipal(principal):
                roles[role] = SettingAsBoolean[setting]

        cache_principal_roles[principal] = roles
        return roles
