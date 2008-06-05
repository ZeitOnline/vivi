# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.component
import zope.app.component.hooks
import zope.app.generations
import zope.app.zopeappgenerations


minimum_generation = 5
generation = 5

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation, generation, "zeit.cms.generation")


def do_evolve(context, evolver):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        evolver(root)
    finally:
        zope.app.component.hooks.setSite(site)
