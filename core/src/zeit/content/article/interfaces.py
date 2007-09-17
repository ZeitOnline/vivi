# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.sources

import zeit.content.image.interfaces

import zeit.content.article.source

ARTICLE_NS = 'http://namespaces.zeit.de/CMS/Article'


class IArticleMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Metadata of an article."""

    classification = zope.schema.FrozenSet(
        title=u"Klassifikation",
        required=False,
        default=frozenset(),
        value_type=zope.schema.Choice(
            source=zeit.cms.content.sources.KeywordSource()))

    commentsAllowed = zope.schema.Bool(
        title=u"Kommentare erlaubt",
        default=True)

    banner = zope.schema.Bool(
        title=u"Banner",
        default=True)

    boxMostRead = zope.schema.Bool(
        title=u"Box „Most Read“",
        default=True)

    navigation = zope.schema.Choice(
        title=u"Navigation",
        source=zeit.cms.content.sources.NavigationSource())

    # references / links to other content

    pageBreak = zope.schema.Int(
        title=u"Seitenumbruch",
        description=u"Absätze pro Seite.",
        min=1,
        default=6)

    dailyNewsletter = zope.schema.Bool(
        title=u"Tages-Newsletter",
        description=(u"Soll der Artikel in den Tages-Newsletter aufgenommen "
                     u"werden?"),
        default=False)

    automaticTeaserSyndication = zope.schema.FrozenSet(
        title=u"Automatische Teaser-Syndizierung",
        description=(u"Beim Checkin werden Teaser in den aktivierten Channels "
                     u"automatisch aktualisiert."),
        default=frozenset(),
        value_type=zope.schema.Choice(
            source=zeit.content.article.source.SyndicatedInSource()))

    images = zope.schema.Tuple(
        title=u'Bilder',
        required=False,
        default=(),
        value_type=zope.schema.Object(
            zeit.content.image.interfaces.IImage))


class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""

    syndicatedIn = zope.schema.FrozenSet(
        title=u"Article is syndicated in these feeds.",
        default=frozenset(),
        value_type=zope.schema.Object(zeit.cms.syndication.interfaces.IFeed))
