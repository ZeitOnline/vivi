# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zeit.cms.generation
import zeit.cms.relation.interfaces

import zeit.content.image.imagereference


def install(root):
    # Add index to find out which objects are referencing images.
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.add_index(zeit.content.image.imagereference.image_referenced_by,
                        multiple=True)

    # Reindex the catalog to have the image index updated
    for obj in relations._catalog:
        relations.index(obj)


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
