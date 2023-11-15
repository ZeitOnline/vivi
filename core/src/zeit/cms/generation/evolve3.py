import zope.component

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.cms.relation.relation
import zeit.cms.relation.interfaces


def update(root):
    relations = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
    relations.add_index(zeit.cms.syndication.feed.syndicated_in, multiple=True)


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
