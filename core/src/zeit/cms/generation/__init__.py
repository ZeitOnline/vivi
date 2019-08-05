import zope.component
import zope.component.hooks
import zope.generations
import zope.app.zopeappgenerations


minimum_generation = generation = 16

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.cms.generation")


def do_evolve(context, evolver):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        evolver(root)
    finally:
        zope.component.hooks.setSite(site)
