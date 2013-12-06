# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.source
import zeit.content.cp.interfaces
import zope.schema

ARTICLE_NS = 'http://namespaces.zeit.de/CMS/Article'


class IArticleMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Metadata of an article."""

    keywords = zeit.cms.tagging.interfaces.Keywords(
        required=False,
        default=())
    keywords.setTaggedValue('zeit.cms.tagging.updateable', True)

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
        default=False,
        required=False)

    artbox_thema = zope.schema.Bool(
        title=_('First related as box'),
        default=False,
        required=False)

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.interfaces.CenterPageSource(),
        required=False)

    # XXX should be Choice with XML-file-backed source (see VIV-241)
    template = zope.schema.TextLine(
        title=_("Template"),
        required=False)

    genre = zope.schema.Choice(
        title=_("Genre"),
        source=zeit.content.article.source.GenreSource(),
        required=False)

    main_image = zope.schema.Choice(
        title=_("Image"),
        description=_("Drag an image here"),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    main_image_layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.article.edit.interfaces.ImageLayoutSource(),
        required=False)

    main_image_block = zope.interface.Attribute(
        u'First block of the body if it is present and is an image block')


class IArticle(IArticleMetadata, zeit.cms.content.interfaces.IXMLContent):
    """Article is the main content type in the Zeit CMS."""

    def updateDAVFromXML():
        """Update the DAV properties based on the information in the XML.

        This is useful when importing an article for instance from
        the Content-Drehscheibe, where the only property information we have
        is in the XML and there is no head section.
        """


class IZONArticle(IArticle, zeit.cms.section.interfaces.ISectionMarker):
    pass


class ArticleSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'article'
    check_interfaces = (IArticle,)


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

    def remove(name):
        """Remove recension with given name from container."""


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
        source=zeit.content.article.source.BookRecensionCategories())

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
        source=ArticleSource())


class ITagesspiegelArticle(zope.interface.Interface):
    """Marker for articles imported from Tagesspiegel."""


class ICDSWorkflow(zope.interface.Interface):
    """Special workflow "extension" for CDS."""

    export_cds = zope.schema.Bool(
        title=_("Export to Tagesspiegel"))
