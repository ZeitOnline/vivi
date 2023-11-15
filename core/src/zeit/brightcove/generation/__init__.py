import zope.generations.generations


minimum_generation = 2
generation = 2


manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.brightcove.generation'
)
