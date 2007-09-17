# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.authentication
import zope.app.security.interfaces

import zeit.cms.generation.install


def install(root):
    site_manager = zope.component.getSiteManager()

    auth = zeit.cms.generation.install.installLocalUtility(
        site_manager,
        zope.app.authentication.PluggableAuthentication,
        'authentication',
        zope.app.security.interfaces.IAuthentication)
    auth.authenticatorPlugins = ('ldap', )
    auth.credentialsPlugins = (
        'No Challenge if Authenticated',
        'Zope Realm Basic-Auth')


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
