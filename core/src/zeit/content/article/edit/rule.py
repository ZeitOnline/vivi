import zope.interface

from zeit.edit.rule import glob
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces


@glob(zope.interface.Interface)
def article(context):
    article = zeit.content.article.interfaces.IArticle(context, None)
    return article is not None


@glob(zope.interface.Interface)
def content(context):
    return []


@glob(zeit.content.article.edit.interfaces.IVideo)
def content(context):  # noqa
    return [x for x in [context.video] if x]


@glob(zeit.content.article.edit.interfaces.IReference)
def content(context):  # noqa
    field = zope.interface.implementedBy(type(zope.security.proxy.getObject(context))).get(
        'references'
    )
    if field.required:
        return [context.references]
    else:
        return [x for x in [context.references] if x]


@glob(zeit.content.article.edit.interfaces.IImage)
def content(context):  # noqa
    if context.references.target:
        return [context.references.target]
    else:
        return []


@glob(zeit.content.article.edit.interfaces.IVolume)
def content(context):  # noqa
    if context.references.target:
        return [context.references.target]
    else:
        return []


@glob(zeit.content.article.edit.interfaces.ILayoutable)
def layout(context):
    return context.layout


# Note that layout(Interface) is defined in zeit.content.cp.rule
