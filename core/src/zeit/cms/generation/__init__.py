import zope.component
import zope.component.hooks
import zope.generations.generations
import zope.generations.utility


minimum_generation = generation = 16

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.cms.generation'
)


def do_evolve(context, evolver):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        evolver(root)
    finally:
        zope.component.hooks.setSite(site)
