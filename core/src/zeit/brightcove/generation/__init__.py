# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.generations.generations


minimum_generation = 1
generation = 1


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.brightcove.generation")
