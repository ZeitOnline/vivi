# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import ldapadapter.interfaces
import ldapadapter.utility
import ldappas.authentication

import zope.app.appsetup.product
import zope.app.authentication.interfaces

ldap_config = (zope.app.appsetup.product.getProductConfiguration('zeit.ldap')
               or {})


def ldapAdapterFactory():
    adapter = ldapadapter.utility.LDAPAdapter(
        host=ldap_config.get('host', 'localhost'),
        port=int(ldap_config.get('port', '389')),
        bindDN=unicode(ldap_config.get('bind-dn', ''), 'utf8'),
        bindPassword=unicode(ldap_config.get('bind-password', ''), 'utf8'))
    return adapter


def ldapPluginFactory():
    ldap = ldappas.authentication.LDAPAuthentication()
    ldap.principalIdPrefix = 'ldap.'
    ldap.adapterName = 'zeit.ldapconnection'
    ldap.searchBase = unicode(ldap_config.get('search-base', ''), 'utf8')
    ldap.searchScope = unicode(ldap_config.get('search-scope', ''), 'utf8')
    ldap.loginAttribute = unicode(ldap_config.get('login-attribute', ''),
                                  'utf8')
    ldap.idAttribute = unicode(ldap_config.get('id-attribute', ''), 'utf8')
    ldap.titleAttribute = ldap_config.get('title-attribute')
    return ldap
