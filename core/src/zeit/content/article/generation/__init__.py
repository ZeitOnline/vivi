import zope.app.generations

minimum_generation = 0
generation = 0

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.content.article.generation")
