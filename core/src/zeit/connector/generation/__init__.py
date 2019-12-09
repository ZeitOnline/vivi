import zope.generations.generations

minimum_generation = 6
generation = 6

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.connector.generation")
