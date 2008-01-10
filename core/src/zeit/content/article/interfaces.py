# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.sources
from zeit.cms.i18n import MessageFactory as _

import zeit.content.article.source

ARTICLE_NS = 'http://namespaces.zeit.de/CMS/Article'


class ISyndicationLogType(zope.interface.interfaces.IInterface):
    """Type for syndication logs."""


class ISyndicationEventLog(zope.interface.Interface):

    syndicatedOn = zope.schema.Datetime(
        title=u"Syndication Time",
        readonly=True)

    syndicatedIn = zope.schema.FrozenSet(
        title=u"Syndicated in",
        readonly=True,
        default=frozenset(),
        value_type=zope.schema.Object(zeit.cms.syndication.interfaces.IFeed))


class IArticleMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Metadata of an article."""

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

    textLength = zope.schema.Int(
        title=u'Anschläge',
        required=False)


class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""

    syndicatedIn = zope.schema.FrozenSet(
        title=u"Article is syndicated in these feeds.",
        default=frozenset(),
        value_type=zope.schema.Object(zeit.cms.syndication.interfaces.IFeed))


    syndicationLog = zope.schema.Tuple(
        title=u"Syndication Log",
        default=(),
        value_type=zope.schema.Object(ISyndicationEventLog))
