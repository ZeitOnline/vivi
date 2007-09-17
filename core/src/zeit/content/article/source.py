# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.sourcefactory.contextual

import zeit.content.article.interfaces


class SyndicatedInSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """A source returning the feeds an article is syndicated in."""

    def getValues(self, context):
        if zeit.content.article.interfaces.IArticle.providedBy(context):
            return iter(context.syndicatedIn)
        return []

    def getTitle(self, context, value):
        return value.title
