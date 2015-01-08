# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.generations.generations

minimum_generation = 6
generation = 6

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.connector.generation")
