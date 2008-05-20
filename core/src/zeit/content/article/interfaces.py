# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zc.form.field

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

    has_recensions = zope.schema.Bool(
        title=_('Has recension content'),
        default=False)

    artbox_thema = zope.schema.Bool(
        title=_('First related as box'),
        default=False)


class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""

    syndicatedIn = zope.schema.FrozenSet(
        title=_("Article is syndicated in these feeds."),
        default=frozenset(),
        value_type=zope.schema.Choice(
            source=zeit.cms.syndication.interfaces.feedSource))


    syndicationLog = zope.schema.Tuple(
        title=_("Syndication Log"),
        default=(),
        value_type=zope.schema.Object(ISyndicationEventLog))


class IBookRecensionReadContainer(zope.interface.Interface):
    """Read interface for book recensions."""

    def __getitem__(index):
        """Get recension with given `inded`."""

    def __iter__():
        """Iterate over recensions."""

    def __len__():
        """Return amount of items."""


class IBookRecensionWriteContainer(zope.interface.Interface):
    """Write interface for book recensions."""

    def append(item):
        """Append item to container."""


class IBookRecensionContainer(IBookRecensionReadContainer,
                              IBookRecensionWriteContainer):
    """Book recensions."""


class IBookRecension(zope.interface.Interface):
    """A recension for a book."""

    authors = zope.schema.Tuple(
        title=_('Authors'),
        min_length=1,
        default=(None, ),
        value_type=zope.schema.TextLine(
            title=_('Author')))

    title = zope.schema.TextLine(title=_('Title'))

    info = zope.schema.Text(
        title=_('Info'),
        required=False)

    genre = zope.schema.TextLine(
        title=_('Genre'),
        required=False)

    category = zope.schema.Choice(
        title=_('ZEIT category'),
        source=zeit.content.article.source.BookRecessionCategories())

    age_limit = zope.schema.Int(
        title=_('Agelimit'),
        required=False)

    original_language = zope.schema.TextLine(
        title=_('Original language'),
        required=False)

    translator = zope.schema.TextLine(
        title=_('Translator'),
        required=False)

    publisher = zope.schema.TextLine(
        title=_('Publisher'),
        required=False)

    location = zope.schema.TextLine(
        title=_('book-location', default=u'Location'),
        required=False)

    year = zope.schema.Int(
        title=_('Year'),
        required=False)

    media_type = zope.schema.TextLine(
        title=_('Media type'),
        required=False)

    pages = zope.schema.Int(
        title=_('Pages'),
        required=False)

    price = zope.schema.TextLine(
        title=_('Price (EUR)'),
        required=False)

    raw_data = zope.schema.Text(
        title=_('Raw data'),
        required=False,
        readonly=True)
