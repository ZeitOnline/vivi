from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import collections
import datetime
import re
import json
import six
import zc.sourcefactory.contextual
import zeit.cms.content.field
import zeit.content.article.interfaces
import zeit.content.article.source
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.link.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.jobticker
import zeit.content.portraitbox.interfaces
import zeit.content.video.interfaces
import zeit.content.volume.interfaces
import zeit.edit.interfaces
import zope.schema
import zope.security.proxy
import zeit.content.cp.interfaces
import logging

log = logging.getLogger(__name__)


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

    teaser = zope.schema.Text(
        title=_('Page teaser'),
        required=False)
    teaser.setTaggedValue('zeit.cms.charlimit', 70)

    number = zope.interface.Attribute(
        'The position of this division in the article body (1-based)')


class VideoLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'video-layout-source'
    default_filename = 'article-video-layouts.xml'
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


class AnimationSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = collections.OrderedDict([
        (u'fade-in', _('Fade in')),
    ])


class IImage(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Image"),
        description=_("Drag an image group here"),
        # BBB allow single images
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

    animation = zope.schema.Choice(
        title=_('Animation'),
        source=AnimationSource(),
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
    default_filename = 'article-infobox-layouts.xml'
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


class PortraitboxLayoutSource(zeit.cms.content.sources.SimpleFixedValueSource):

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


class IRawText(zeit.content.modules.interfaces.IRawText):
    pass


class IEmbed(zeit.content.modules.interfaces.IEmbed):
    pass


class AvailableBlockLayoutSource(BodyAwareXMLSource):
    """
    Superclass for articleblocklayouts, which can be defined via XML
    """
    product_configuration = 'zeit.content.article'
    attribute = 'id'


class CitationLayoutSource(AvailableBlockLayoutSource):

    config_url = 'citation-layout-source'
    default_filename = 'article-citation-layouts.xml'


CITATION_LAYOUT_SOURCE = CitationLayoutSource()


class CitationCommentLayoutSource(AvailableBlockLayoutSource):

    config_url = 'citation-layout-source'
    default_filename = 'article-citation-layouts.xml'


CITATIONCOMMENT_LAYOUT_SOURCE = CitationCommentLayoutSource()


class BoxLayoutSource(AvailableBlockLayoutSource):

    # If we want to check if the box is of a certain type (like infobox)
    # We could change this behaviour of isAvailable to check for a type as well
    # and maybe get rid of the superclass

    config_url = 'box-layout-source'
    default_filename = 'article-box-layouts.xml'


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


class ICitationComment(zeit.edit.interfaces.IBlock):

    text = zope.schema.Text(
        title=_('Citation Comment'))

    url = zope.schema.URI(
        title=_('URL'),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=CITATIONCOMMENT_LAYOUT_SOURCE,
        default=u'default',
        required=False)


class LiveblogVersions(zeit.cms.content.sources.SimpleFixedValueSource):

    values = collections.OrderedDict([
        (u'3', '3'),
    ])


class ILiveblog(zeit.edit.interfaces.IBlock):

    blog_id = zope.schema.TextLine(
        title=_('Liveblog id'))

    version = zope.schema.Choice(
        title=_('Liveblog version'),
        source=LiveblogVersions(),
        default=u'3',
        required=False)

    collapse_preceding_content = zope.schema.Bool(
        title=_('Collapse preceding content'),
        default=True,
        required=False)


class ICardstack(zeit.edit.interfaces.IBlock):

    card_id = zope.schema.TextLine(
        title=_('Cardstack id'))
    is_advertorial = zope.schema.Bool(
        title=_('Advertorial?'),
        default=False)


class IQuiz(zeit.content.modules.interfaces.IQuiz):
    # XXX Need to inerit our own interface, otherwise our UI bleeds into z.c.cp
    pass


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


class IMail(zeit.content.modules.interfaces.IMail):
    pass


class IBreakingNewsBody(zope.interface.Interface):

    text = zope.schema.Text(
        title=_('Article body'),
        default=_('breaking-news-more-shortly'),
        required=False)


class AdplaceTileSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = collections.OrderedDict([
        (u'desktop_3', 'Desktop: 3'),
        (u'desktop_4', 'Desktop: 4'),
        (u'desktop_5', 'Desktop: 5'),
        (u'desktop_8', 'Desktop: 8'),
        (u'desktop_41', 'Desktop: 41'),
        (u'desktop_42', 'Desktop: 42'),
        (u'desktop_43', 'Desktop: 43'),
        (u'mobile_1', 'Mobile: 1'),
        (u'mobile_3', 'Mobile: 3'),
        (u'mobile_4', 'Mobile: 4'),
        (u'mobile_41', 'Mobile: 41'),
        (u'mobile_42', 'Mobile: 42'),
        (u'mobile_43', 'Mobile: 43'),
        (u'ctm', 'Content Marketing Teaser Mobil / Desktop'),
        (u'special', 'Desktop: 3 und Mobil: 1')
    ])


class IAdplace(zeit.edit.interfaces.IBlock):

    tile = zope.schema.Choice(
        title=_('Adplace Tile'),
        required=True,
        source=AdplaceTileSource())


class IPuzzle(zope.interface.Interface):
    """A puzzle type"""

    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    multiple = zope.interface.Attribute('Has multiple episodes')


class Puzzle(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, multiple):
        super(Puzzle, self).__init__(id, title, None)
        self.multiple = multiple


class PuzzleSource(zeit.cms.content.sources.ObjectSource,
                   zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'puzzleforms-source'
    default_filename = 'puzzleforms.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            puzzle = Puzzle(
                six.text_type(node.get('id')),
                six.text_type(node.text.strip()),
                node.get('multiple') == u'true'
            )
            result[puzzle.id] = puzzle
        return result

    def getTitle(self, context, value):
        return value.title


PUZZLE_SOURCE = PuzzleSource()


class IPuzzleForm(zeit.edit.interfaces.IBlock):

    puzzle_type = zope.schema.Choice(
        title=_('Puzzle'),
        required=True,
        source=PUZZLE_SOURCE)

    year = zope.schema.Int(
        title=_('Year'),
        min=datetime.date.today().year,
        default=datetime.date.today().year,
    )


class TopicpageFilterSource(zc.sourcefactory.basic.BasicSourceFactory,
                            zeit.cms.content.sources.CachedXMLBase):

    COMMENT = re.compile(r'\s*//')

    product_configuration = 'zeit.content.cp'
    config_url = 'topicpage-filter-source'
    default_filename = 'topicpage-filters.json'

    def json_data(self):
        result = collections.OrderedDict()
        for row in self._get_tree():
            if len(row) != 1:
                continue
            key = list(row.keys())[0]
            result[key] = row[key]
        return result

    @CONFIG_CACHE.cache_on_arguments()
    def _get_tree_from_url(self, url):
        try:
            data = []
            for line in six.moves.urllib.request.urlopen(url):
                line = six.ensure_text(line)
                if self.COMMENT.search(line):
                    continue
                data.append(line)
            data = '\n'.join(data)
            return json.loads(data)
        except Exception:
            log.warning(
                'TopicpageFilterSource could not parse %s', url, exc_info=True)
            return {}

    def getValues(self):
        return self.json_data().keys()

    def getTitle(self, value):
        return self.json_data()[value].get('title', value)

    def getToken(self, value):
        return value


class TopicboxSourceType(zeit.content.cp.interfaces.SimpleDictSource):

    values = collections.OrderedDict([
        ('manuell', _('manuell')),
        ('centerpage', _('automatic-area-type-centerpage')),
        ('topicpage', _('automatic-area-type-topicpage')),
        ('elasticsearch-query', _('automatic-area-type-elasticsearch-query')),
        ('related-api', _('tms-related-api'))
    ])


class TopicReferenceSource(zeit.cms.content.contentsource.CMSContentSource):

    def __init__(self, allow_cp=False):
        self.allow_cp = allow_cp
        self._allowed_interfaces = (
            zeit.content.article.interfaces.IArticle,
            zeit.content.gallery.interfaces.IGallery,
            zeit.content.link.interfaces.ILink)

    @property
    def check_interfaces(self):
        if not self.allow_cp:
            return self._allowed_interfaces
        return self._allowed_interfaces + (
            zeit.content.cp.interfaces.ICenterPage, )


class ITopicbox(zeit.edit.interfaces.IBlock):
    """
    Element which references other Articles
    """

    supertitle = zope.schema.TextLine(
        title=_('Supertitle'),
        description=_('Please take care of capitalisation.'),
        max_length=30)

    title = zope.schema.TextLine(
        title=_("Title"),
        max_length=30)

    first_reference = zope.schema.Choice(
        title=_("Reference"),
        description=_("Drag article/cp/link here"),
        source=TopicReferenceSource(allow_cp=True))

    second_reference = zope.schema.Choice(
        title=_("Reference"),
        description=_("Drag article/link here"),
        source=TopicReferenceSource(),
        required=False)

    third_reference = zope.schema.Choice(
        title=_("Reference"),
        description=_("Drag article/link here"),
        source=TopicReferenceSource(),
        required=False)

    link = zope.schema.TextLine(
        title=_('Link'),
        required=False)

    link_text = zope.schema.TextLine(
        title=_("Linktext"),
        required=False,
        max_length=30)

    referenced_cp = zope.interface.Attribute(
        'Referenced CP or None')

    elasticsearch_raw_query = zope.schema.Text(
        title=_('Elasticsearch raw query'),
        required=False)

    elasticsearch_raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'payload.document.date_first_released:desc',
        required=False)

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    is_complete_query = zope.schema.Bool(
        title=_('Take over complete query body'),
        description=_('Remember to add payload.workflow.published:true'),
        default=False,
        required=False)

    centerpage = zope.schema.Choice(
        title=_('Get teasers from CenterPage'),
        source=zeit.content.cp.source.centerPageSource,
        required=False)

    source_type = zope.schema.Choice(
        title=_('source-type'),
        source=TopicboxSourceType(),
        required=True,
        default='centerpage')

    topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage'),
        required=False)

    topicpage_filter = zope.schema.Choice(
        title=_('Topicpage filter'),
        source=TopicpageFilterSource(),
        required=False)

    count = zope.schema.Int(title=_('Amount of teasers'), default=3)

    def values():
        """
        Iterable of ICMSContent
        """


class IContentQuery(zope.interface.Interface):
    """Mechanism to retrieve content objects.
    Used to register named adapters for the different IArea.automatic_types.
    """

    def __call__(self):
        """Returns list of content objects."""


class INewsletterSignup(zeit.content.modules.interfaces.INewsletterSignup):
    pass


class IRecipeList(zeit.content.modules.interfaces.IRecipeList):
    pass


class IIngredientDice(zeit.edit.interfaces.IBlock):
    """A simple block without any customisation.
    If something like article-extras would exist this should be one.
    """

    pass
