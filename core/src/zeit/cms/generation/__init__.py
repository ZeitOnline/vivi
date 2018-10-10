import decorator

import zope.app.component
import zope.app.component.hooks
import zope.generations
import zope.app.zopeappgenerations


minimum_generation = generation = 16

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.cms.generation")


def do_evolve(context, evolver):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        evolver(root)
    finally:
        zope.app.component.hooks.setSite(site)


# XXX do_evolve should be phased out and implemented as the decorator itself.

@decorator.decorator
def get_root(evolver, context):
    do_evolve(context, evolver)
