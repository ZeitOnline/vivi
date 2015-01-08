import zope.app.generations.generations


minimum_generation = 2
generation = 2


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.brightcove.generation")
