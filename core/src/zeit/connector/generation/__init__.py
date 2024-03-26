import zope.generations.generations


minimum_generation = 8
generation = 8

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.connector.generation'
)
