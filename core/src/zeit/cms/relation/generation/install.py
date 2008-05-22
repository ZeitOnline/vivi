# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations

import zeit.cms.generation.install

import zeit.relation.interfaces
import zeit.relation.relation


def related(content, catalog):
    related = zeit.cms.content.interfaces.IRelatedContent(content, None)
    if related is None:
        return None
    return related.related


def install(root):
    site_manager = zope.component.getSiteManager()
    relations = zeit.cms.generation.install.installLocalUtility(
        site_manager,
        zeit.relation.relation.Relations,
        'relations',
        zeit.relation.interfaces.IRelations)
    relations.add_index(related, multiple=True)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
