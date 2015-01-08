import zope.app.generations


minimum_generation = 1
generation = 1

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.content.image.generation")
