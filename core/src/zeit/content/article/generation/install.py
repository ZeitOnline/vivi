# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation.install
import zope.app.component
import zope.app.component.hooks
import zope.app.zopeappgenerations


def install(root):
    site_manager = zope.component.getSiteManager()
    name = u'Article templates'
    templates = zope.component.getUtility(
        zeit.cms.content.interfaces.ITemplateManagerContainer)
    zeit.cms.generation.install.installLocalUtility(
        templates, zeit.cms.content.template.TemplateManager,
        name, zeit.cms.content.interfaces.ITemplateManager,
        utility_name=name)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
