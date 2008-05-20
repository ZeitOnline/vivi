# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zc.sourcefactory.contextual

import zeit.content.article.interfaces
import zeit.cms.content.interfaces


class SyndicatedInSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """A source returning the feeds an article is syndicated in."""

    def getValues(self, context):
        if zeit.content.article.interfaces.IArticle.providedBy(context):
            return iter(context.syndicatedIn)
        return []

    def getTitle(self, context, value):
        return value.title


class BookRecessionCategories(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'source-book-recession-categories'
