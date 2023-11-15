import zeit.brightcove.interfaces
import zeit.cms.generation
import zope.component


def update(root):
    repository = zope.component.getUtility(zeit.brightcove.interfaces.IRepository)
    for key, value in repository.items():
        value.__name__ = key
        value.__parent__ = repository


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
