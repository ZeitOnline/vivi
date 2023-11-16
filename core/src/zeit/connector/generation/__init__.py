import zope.generations.generations

minimum_generation = 7
generation = 7

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.connector.generation'
)
