from zeit.edit.rule import glob
import zeit.content.article.interfaces
import zeit.content.article.edit.interfaces
import zope.interface


@glob(zope.interface.Interface)
def article(context):
    article = zeit.content.article.interfaces.IArticle(context, None)
    return article is not None


@glob(zope.interface.Interface)
def content(context):
    return []


@glob(zeit.content.article.edit.interfaces.IVideo)  # noqa
def content(context):
    return [x for x in [context.video] if x]


@glob(zeit.content.article.edit.interfaces.IReference)  # noqa
def content(context):
    field = zope.interface.implementedBy(type(
        zope.security.proxy.getObject(context))).get('references')
    if field.required:
        return [context.references]
    else:
        return [x for x in [context.references] if x]


@glob(zeit.content.article.edit.interfaces.IImage)  # noqa
def content(context):
    if context.references.target:
        return [context.references.target]
    else:
        return []


@glob(zeit.content.article.edit.interfaces.IVolume)  # noqa
def content(context):
    if context.references.target:
        return [context.references.target]
    else:
        return []


@glob(zeit.content.article.edit.interfaces.ILayoutable)
def layout(context):
    return context.layout

# layout(Interface) is defined in zeit.content.cp.rule
