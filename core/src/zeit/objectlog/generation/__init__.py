import zope.generations.generations


minimum_generation = 1
generation = 1

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.objectlog.generation'
)
