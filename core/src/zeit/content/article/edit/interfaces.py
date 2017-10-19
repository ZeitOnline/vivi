from zeit.content.article.i18n import MessageFactory as _
import collections
import zc.sourcefactory.basic
import zeit.cms.content.field
import zeit.content.article.interfaces
import zeit.content.article.source
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.modules.jobticker
import zeit.content.portraitbox.interfaces
import zeit.content.text.interfaces
import zeit.content.video.interfaces
import zeit.content.volume.interfaces
import zeit.edit.interfaces
import zope.schema


class IArticleArea(zeit.edit.interfaces.IArea):
    pass


class IEditableBody(IArticleArea):
    """Editable representation of an article's body."""

    def ensure_division():
        """Make sure the body contains a division.

        If there is no <division> in the body, update XML by creating a
        division for every 7 body elements and moving them into the created
        divisions.

        """


class IReadHeaderArea(zeit.edit.interfaces.IReadContainer):

    module = zope.interface.Attribute(
        'Convenience access for self.values()[0] or None')


class IWriteHeaderArea(zeit.edit.interfaces.IWriteContainer):

    def clear():
        """Delete all contained modules."""


class IHeaderArea(
        IReadHeaderArea,
        IWriteHeaderArea,
        IArticleArea):
    """Separate area for header that may contain one module."""


class IFindReplace(zope.interface.Interface):
    """Find/replace functionality for IEditableBody."""

    def replace_all(find, replace):
        """Replace the ``find`` text with ``replace`` in all text IBlocks."""


class ILayoutable(zope.interface.Interface):
    """A block with layout information."""

    layout = zope.interface.Attribute(
        "Layout should be a string, limitations etc. defined on  more specific"
        " interfaces")


class IParagraph(zeit.edit.interfaces.IBlock):
    """<p/> element."""

    text = zope.schema.Text(title=_('Paragraph-Text'))


class IUnorderedList(IParagraph):
    """<ul/> element."""


class IOrderedList(IParagraph):
    """<ol/> element."""


class IIntertitle(IParagraph):
    """<intertitle/> element."""


class BodyAwareXMLSource(zeit.cms.content.sources.XMLSource):

    def isAvailable(self, node, context):
        context = zeit.content.article.interfaces.IArticle(context, None)
        return super(BodyAwareXMLSource, self).isAvailable(node, context)


class IDivision(zeit.edit.interfaces.IBlock):
    """<division/> element"""

    teaser = zope.schema.TextLine(
        title=_('Page teaser'),
        required=False)

    number = zope.interface.Attribute(
        'The position of this division in the article body (1-based)')


class LayoutSourceBase(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]


class VideoLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'video-layout-source'
    attribute = 'id'


class IVideo(zeit.edit.interfaces.IBlock, ILayoutable):

    video = zope.schema.Choice(
        title=_('Video'),
        description=_("Drag a video here"),
        required=False,
        source=zeit.content.video.interfaces.videoOrPlaylistSource)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=VideoLayoutSource(),
        default=u'large',
        required=False)

    # XXX it would be nice if could somehow express that IVideo actually
    # is a kind of IReference (only it has video/video_2 instead of references)
    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'),
        required=False,
        default=True)


class IReference(zeit.edit.interfaces.IBlock):
    """A block which references another object."""

    references = zope.schema.Field(
        title=_('Referenced object.'),
        required=False)

    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'),
        required=False,
        default=True)


class IImage(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Image"),
        description=_("Drag an image group here"),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    set_manually = zope.schema.Bool(
        title=_("Edited"),
        required=False,
        default=False)

    display_mode = zope.schema.Choice(
        title=_('Display Mode'),
        source=zeit.content.article.source.IMAGE_DISPLAY_MODE_SOURCE,
        default=u'column-width',
        required=False)

    # Currently need default for bw compat.
    variant_name = zope.schema.Choice(
        title=_('Variant Name'),
        source=zeit.content.article.source.IMAGE_VARIANT_NAME_SOURCE,
        default=u'wide',
        required=False)


class IGallery(IReference):
    """block for <gallery/> tags."""

    references = zope.schema.Choice(
        title=_('Gallery'),
        description=_("Drag an image gallery here"),
        source=zeit.content.gallery.interfaces.gallerySource,
        required=False)


class InfoboxLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'infobox-layout-source'
    attribute = 'id'


class IInfobox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Infobox'),
        description=_("Drag an infobox here"),
        source=zeit.content.infobox.interfaces.infoboxSource,
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=InfoboxLayoutSource(),
        required=False,
        default=u'default')


class PortraitboxLayoutSource(LayoutSourceBase):

    values = collections.OrderedDict([
        (u'short', _('short')),
        (u'wide', _('wide')),
    ])


class IPortraitbox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Portraitbox'),
        description=_("Drag a portraitbox here"),
        source=zeit.content.portraitbox.interfaces.portraitboxSource,
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=PortraitboxLayoutSource(),
        required=False,
        default=u'short')

    name = zope.schema.TextLine(
        title=_('First and last name'),
        required=False)

    text = zope.schema.Text(
        title=_('Text'),
        required=False)


class IAuthor(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Author"),
        description=_("Drag an author here"),
        source=zeit.cms.content.interfaces.authorSource,
        required=False)


class IVolume(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Volume"),
        description=_("Drag a volume here"),
        source=zeit.content.volume.interfaces.VOLUME_SOURCE,
        required=False)


def validate_rawxml(xml):
    if xml.tag != 'raw':
        raise zeit.cms.interfaces.ValidationError(
            _("The root element must be <raw>."))
    return True


class IRawXML(zeit.edit.interfaces.IBlock):

    xml = zeit.cms.content.field.XMLTree(
        title=_('XML source'),
        tidy_input=True,
        constraint=validate_rawxml)


class IRawText(zeit.edit.interfaces.IBlock):

    text_reference = zope.schema.Choice(
        title=_("Raw text reference"),
        source=zeit.content.text.interfaces.textSource,
        required=False)

    text = zope.schema.Text(
        title=_('Raw text'),
        required=False)


class AvailableBlockLayoutSource(zeit.cms.content.sources.XMLSource):
    """
    Superclass for articleblocklayouts, which can be defined via XML
    """
    product_configuration = 'zeit.content.article'
    attribute = 'id'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(AvailableBlockLayoutSource,
                     self).isAvailable(node, article)


class CitationLayoutSource(AvailableBlockLayoutSource):

    config_url = 'citation-layout-source'

CITATION_LAYOUT_SOURCE = CitationLayoutSource()


class BoxLayoutSource(AvailableBlockLayoutSource):

    # If we want to check if the box is of a certain type (like infobox)
    # We could change this behaviour of isAvailable to check for a type as well
    # and maybe get rid of the superclass

    config_url = 'box-layout-source'

BOX_LAYOUT_SOURCE = BoxLayoutSource()


class ICitation(zeit.edit.interfaces.IBlock):

    text = zope.schema.Text(
        title=_('Citation'))

    attribution = zope.schema.TextLine(
        title=_('Attribution'),
        required=False)

    url = zope.schema.URI(
        title=_('URL'),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=CITATION_LAYOUT_SOURCE,
        default=u'default',
        required=False)


class ILiveblog(zeit.edit.interfaces.IBlock):

    blog_id = zope.schema.TextLine(
        title=_('Liveblog id'))


class ICardstack(zeit.edit.interfaces.IBlock):

    card_id = zope.schema.TextLine(
        title=_('Cardstack id'))
    is_advertorial = zope.schema.Bool(
        title=_('Advertorial?'),
        default=False)


class IQuiz(zeit.edit.interfaces.IBlock):

    quiz_id = zope.schema.TextLine(
        title=_('Quiz id'))
    adreload_enabled = zope.schema.Bool(
        title=_('Enable adreload'),
        default=True)


class IPodcast(zeit.edit.interfaces.IBlock):

    episode_id = zope.schema.TextLine(
        title=_('Podcast id'))


class IBox(zeit.edit.interfaces.IBlock):
    """
    This box is a first step to generalizing other boxes
    (infobox, portraitbox...). Another field, the body, should be added, which
    has the ability to contain other content, like additional images.
    """

    supertitle = zope.schema.TextLine(
        title=_('Supertitle'),
        description=_('Please take care of capitalisation.'),
        required=False,
        max_length=70)

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False,
        max_length=70)

    subtitle = zope.schema.Text(
        title=_("Subtitle"),
        required=False
    )

    layout = zope.schema.Choice(
        title=_('Layout'),
        required=True,
        source=BOX_LAYOUT_SOURCE
    )


JOBTICKER_SOURCE = zeit.content.modules.jobticker.FeedSource(
    zeit.content.article.interfaces.IArticle)


class IJobTicker(zeit.content.modules.interfaces.IJobTicker):

    feed = zope.schema.Choice(
        title=_('Jobbox ticker'),
        required=True,
        source=JOBTICKER_SOURCE)


class IBreakingNewsBody(zope.interface.Interface):

    text = zope.schema.Text(
        title=_('Article body'),
        default=_('breaking-news-more-shortly'),
        required=False)

    article_id = zope.interface.Attribute(
        'The uniqueID of the breaking news article')
