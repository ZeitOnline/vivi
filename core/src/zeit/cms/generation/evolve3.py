import zeit.cms.generation
import zeit.cms.generation.install


def update(root):
    return
    # relations = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
    # relations.add_index(zeit.cms.syndication.feed.syndicated_in, multiple=True)


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
