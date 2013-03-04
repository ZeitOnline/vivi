# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

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


@glob(zeit.content.article.edit.interfaces.IVideo)
def content(context):
    return filter(None, [context.video, context.video_2])


@glob(zeit.content.article.edit.interfaces.IReference)
def content(context):
    return [context.references]


@glob(zeit.content.article.edit.interfaces.ILayoutable)
def layout(context):
    return context.layout

# layout(Interface) is defined in zeit.content.cp.rule
