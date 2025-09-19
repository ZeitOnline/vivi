import zope.component
import zope.component.hooks
import zope.generations.generations
import zope.generations.utility


minimum_generation = 1
generation = 1

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.objectlog.generation'
)


def do_evolve(context, func):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        func(root)
    finally:
        zope.component.hooks.setSite(site)
