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
import zope.securitypolicy.zopepolicy


class SecurityPolicy(zope.securitypolicy.zopepolicy.ZopeSecurityPolicy):
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

        parent = removeSecurityProxy(getattr(parent, '__parent__', None))
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

        roles = self.cached_roles(
            removeSecurityProxy(getattr(parent, '__parent__', None)), permission
        )
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
            removeSecurityProxy(getattr(parent, '__parent__', None)), principal
        )

        prinrole = IPrincipalRoleMap(parent, None)
        if prinrole:
            roles = roles.copy()
            for role, setting in prinrole.getRolesForPrincipal(principal):
                roles[role] = SettingAsBoolean[setting]

        cache_principal_roles[principal] = roles
        return roles
