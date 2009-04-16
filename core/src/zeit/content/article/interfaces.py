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
from zeit.content.article.i18n import MessageFactory as _

import zeit.content.article.source

ARTICLE_NS = 'http://namespaces.zeit.de/CMS/Article'


class IArticleMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Metadata of an article."""

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

    textLength = zope.schema.Int(
        title=_('Textlength'),
        required=False)

    has_recensions = zope.schema.Bool(
        title=_('Has recension content'),
        default=False)

    artbox_thema = zope.schema.Bool(
        title=_('First related as box'),
        default=False)

    export_cds = zope.schema.Bool(
        title=_("Export to Tagesspiegel"),
        default=True)

class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""


    def updateDAVFromXML():
        """Update the DAV properties based on the information in the XML.

        This is useful when importing an article for instance from
        the Content-Drehscheibe, where the only property information we have
        is in the XML and there is no head section.
        """

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


class IAggregatedComments(zope.interface.Interface):

    comment_id = zope.schema.Choice(
        title=_('Aggregate comments'),
        description=_('aggregate-comments-description'),
        required=False,
        source=zeit.cms.content.contentsource.cmsContentSource)
