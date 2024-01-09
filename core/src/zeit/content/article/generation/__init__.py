import zope.generations.generations


minimum_generation = 0
generation = 0

manager = zope.generations.generations.SchemaManager(
    minimum_generation, generation, 'zeit.content.article.generation'
)
