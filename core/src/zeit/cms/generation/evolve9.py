# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.relation.relation import _dump_content, _load_content
import BTrees
import zc.relation.catalog
import zeit.cms.generation
import zope.component


def update(root):
    # we must use a new catalog since simply adding a new index to an existing
    # catalog triggers a full reindex, which is too expensive
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    # XXX remove old catalog in a later generation (after migrating)
    relations._catalog_generation8 = relations._catalog
    relations._catalog = zc.relation.catalog.Catalog(
        _dump_content, _load_content, btree=BTrees.family32.OI)
    relations.add_index(
        zeit.cms.relation.relation.referenced_by, multiple=True)


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
