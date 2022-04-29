import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation.install
import zope.component
import zope.component.hooks
import zope.generations.utility


def install(root):
    name = 'Article templates'
    templates = zope.component.getUtility(
        zeit.cms.content.interfaces.ITemplateManagerContainer)
    zeit.cms.generation.install.installLocalUtility(
        templates, zeit.cms.content.template.TemplateManager,
        name, zeit.cms.content.interfaces.ITemplateManager,
        utility_name=name)


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        install(root)
    finally:
        zope.component.hooks.setSite(site)
