# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.generations

minimum_generation = 5
generation = 5

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.connector.generation")
