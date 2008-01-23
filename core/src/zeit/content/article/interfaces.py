# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
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
        title=_("Syndication Time"),
        readonly=True)

    syndicatedIn = zope.schema.FrozenSet(
        title=_("Syndicated in"),
        readonly=True,
        default=frozenset(),
        value_type=zope.schema.Object(zeit.cms.syndication.interfaces.IFeed))


class IArticleMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Metadata of an article."""

    commentsAllowed = zope.schema.Bool(
        title=_("Comments allowed"),
        default=True)

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=True)

    boxMostRead = zope.schema.Bool(
        title=_("Box Most Read"),
        default=True)

    # references / links to other content

    pageBreak = zope.schema.Int(
        title=_("Pagebreak"),
        description=_("Paragraphs per page until a pagebreak."),
        min=1,
        default=6)

    paragraphs = zope.schema.Int(
        title=_("Paragraphsamount"),
        description=_("Amount of paragraphs in total."),
        readonly=True,
        required=False)

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily Newsletter"),
        description=_(
            "Should this article be listed in the daily newsletter?"),
        default=False)

    automaticTeaserSyndication = zope.schema.FrozenSet(
        title=_("Automatic Teasersyndication"),
        description=_(
            "Teaser will automatically be updated in the enabled channels."),
        default=frozenset(),
        value_type=zope.schema.Choice(
            source=zeit.content.article.source.SyndicatedInSource()))

    textLength = zope.schema.Int(
        title=_('Textlength'),
        required=False)


class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""

    syndicatedIn = zope.schema.FrozenSet(
        title=_("Article is syndicated in these feeds."),
        default=frozenset(),
        value_type=zope.schema.Object(zeit.cms.syndication.interfaces.IFeed))


    syndicationLog = zope.schema.Tuple(
        title=_("Syndication Log"),
        default=(),
        value_type=zope.schema.Object(ISyndicationEventLog))
