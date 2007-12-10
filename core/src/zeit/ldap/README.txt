=========
Zeit LDAP
=========

The `zeit.ldap` package connects the cms to an LDAP or ADS server. A pluggable
authentication utility is registered and configured for using ldap[1]_::

    >>> import zope.component
    >>> import zope.app.security.interfaces
    >>> pas = zope.component.getUtility(
    ...     zope.app.security.interfaces.IAuthentication)
    >>> pas
    <zope.app.authentication.authentication.PluggableAuthentication object at 0x...>

The authentication uses the ldap plugin::

    >>> pas.authenticatorPlugins
    ('ldap',)
    >>> plugins = list(pas.getAuthenticatorPlugins())
    >>> plugins
    [('ldap', <ldappas.authentication.LDAPAuthentication object at 0x...>)]
    >>> ldap = plugins[0][1]
    >>> ldap
    <ldappas.authentication.LDAPAuthentication object at 0x...>


So the ldap is basically configured correctly[2]_.



.. [1]  We need to set the site here::

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())
    

.. [2] Cleanup

    >>> zope.app.component.hooks.setSite(old_site)
