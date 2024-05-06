import collections
import datetime
import logging

import pendulum
import zc.sourcefactory.contextual
import zope.schema
import zope.security.proxy

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
from zeit.content.animation.interfaces import IAnimation
from zeit.content.article.source import BodyAwareXMLSource
import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.content.article.interfaces
import zeit.content.article.source
import zeit.content.audio.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.link.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.jobticker
import zeit.content.portraitbox.interfaces
import zeit.content.video.interfaces
import zeit.content.volume.interfaces
import zeit.contentquery.interfaces
import zeit.edit.interfaces


log = logging.getLogger(__name__)


class IElement(zeit.edit.interfaces.IElement):
    pass


class IArticleArea(zeit.edit.interfaces.IArea, IElement):
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
    module = zope.interface.Attribute('Convenience access for self.values()[0] or None')


class IWriteHeaderArea(zeit.edit.interfaces.IWriteContainer):
    def clear():
        """Delete all contained modules."""


class IHeaderArea(IReadHeaderArea, IWriteHeaderArea, IArticleArea):
    """Separate area for header that may contain one module."""


class IFindReplace(zope.interface.Interface):
    """Find/replace functionality for IEditableBody."""

    def replace_all(find, replace):
        """Replace the ``find`` text with ``replace`` in all text IBlocks."""


class ILayoutable(zope.interface.Interface):
    """A block with layout information."""

    layout = zope.interface.Attribute(
        'Layout should be a string, limitations etc. defined on  more specific' ' interfaces'
    )


class IBlock(IElement, zeit.edit.interfaces.IBlock, zeit.edit.interfaces.IFoldable):
    pass


class IParagraph(IBlock):
    """<p/> element."""

    text = zope.schema.Text(title=_('Paragraph-Text'))


class IUnorderedList(IParagraph):
    """<ul/> element."""


class IOrderedList(IParagraph):
    """<ol/> element."""


class IIntertitle(IParagraph):
    """<intertitle/> element."""


class IDivision(IBlock):
    """<division/> element"""

    teaser = zope.schema.Text(title=_('Page teaser'), required=False)
    teaser.setTaggedValue('zeit.cms.charlimit', 70)

    number = zope.interface.Attribute('The position of this division in the article body (1-based)')


class VideoLayoutSource(BodyAwareXMLSource):
    product_configuration = 'zeit.content.article'
    config_url = 'video-layout-source'
    default_filename = 'article-video-layouts.xml'
    attribute = 'id'


class IVideo(IBlock, ILayoutable):
    video = zope.schema.Choice(
        title=_('Video'),
        description=_('Drag a video here'),
        required=False,
        source=zeit.content.video.interfaces.videoSource,
    )

    layout = zope.schema.Choice(
        title=_('Layout'), source=VideoLayoutSource(), default='large', required=False
    )

    # XXX it would be nice if could somehow express that IVideo actually
    # is a kind of IReference (only it has video/video_2 instead of references)
    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'), required=False, default=True
    )


class IVideoTagesschauSource(zope.schema.interfaces.IIterableSource):
    pass


class VideoTagesschauSelection(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    @zope.interface.implementer(IVideoTagesschauSource)
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        pass

    def getValues(self, context):
        return context.tagesschauvideos.values()

    def getTitle(self, context, value):
        date_published = pendulum.parse(value.date_published).to_datetime_string()
        label = '<strong>%s</strong> - %s (%s)<br />' '<a href="%s" target="_blank">%s</a>' % (
            value.title,
            date_published,
            value.type,
            value.video_url_hd,
            _('open video'),
        )
        return label

    def getToken(self, context, value):
        return value.id


class IVideoTagesschau(IBlock):
    """Block for placing 'Tagesschau' Video in article"""

    tagesschauvideo = zope.schema.Choice(
        title=_('Select video'), source=VideoTagesschauSelection(), required=False
    )

    tagesschauvideos = zope.interface.Attribute('List of available videos')


class IVideoTagesschauAPI(zope.interface.Interface):
    def request_videos(self):
        """call Tagesschau API"""


class IReference(IBlock):
    """A block which references another object."""

    references = zope.schema.Field(title=_('Referenced object.'), required=False)

    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'), required=False, default=True
    )


class AnimationSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = collections.OrderedDict(
        [
            ('fade-in', _('Fade in')),
        ]
    )


class IImage(IReference):
    references = zeit.cms.content.interfaces.ReferenceField(
        title=_('Image'),
        description=_('Drag an image group here'),
        # BBB allow single images
        source=zeit.content.image.interfaces.imageSource,
        required=False,
    )

    set_manually = zope.schema.Bool(title=_('Edited'), required=False, default=False)

    display_mode = zope.schema.Choice(
        title=_('Display Mode'),
        source=zeit.content.article.source.IMAGE_DISPLAY_MODE_SOURCE,
        default='column-width',
        required=False,
    )

    # Currently need default for bw compat.
    variant_name = zope.schema.Choice(
        title=_('Variant Name'),
        source=zeit.content.article.source.IMAGE_VARIANT_NAME_SOURCE,
        default='wide',
        required=False,
    )

    animation = zope.schema.Choice(title=_('Animation'), source=AnimationSource(), required=False)


class IGallery(IReference):
    """block for <gallery/> tags."""

    references = zope.schema.Choice(
        title=_('Gallery'),
        description=_('Drag an image gallery here'),
        source=zeit.content.gallery.interfaces.gallerySource,
        required=False,
    )


class InfoboxLayoutSource(BodyAwareXMLSource):
    product_configuration = 'zeit.content.article'
    config_url = 'infobox-layout-source'
    default_filename = 'article-infobox-layouts.xml'
    attribute = 'id'


class IInfobox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Infobox'),
        description=_('Drag an infobox here'),
        source=zeit.content.infobox.interfaces.infoboxSource,
        required=False,
    )

    layout = zope.schema.Choice(
        title=_('Layout'), source=InfoboxLayoutSource(), required=False, default='default'
    )


class PortraitboxLayoutSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = collections.OrderedDict(
        [
            ('short', _('short')),
            ('wide', _('wide')),
        ]
    )


class IPortraitbox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Portraitbox'),
        description=_('Drag a portraitbox here'),
        source=zeit.content.portraitbox.interfaces.portraitboxSource,
        required=False,
    )

    layout = zope.schema.Choice(
        title=_('Layout'), source=PortraitboxLayoutSource(), required=False, default='short'
    )

    name = zope.schema.TextLine(title=_('First and last name'), required=False)

    text = zope.schema.Text(title=_('Text'), required=False)


class IAuthor(IReference):
    references = zeit.cms.content.interfaces.ReferenceField(
        title=_('Author'),
        description=_('Drag an author here'),
        source=zeit.cms.content.interfaces.authorSource,
        required=False,
    )


class IVolume(IReference):
    references = zeit.cms.content.interfaces.ReferenceField(
        title=_('Volume'),
        description=_('Drag a volume here'),
        source=zeit.content.volume.interfaces.VOLUME_SOURCE,
        required=False,
    )


class IAudio(IBlock):
    references = zope.schema.Choice(
        title=_('Drag an audio here'),
        source=zeit.content.audio.interfaces.AudioSource(),
    )


def validate_rawxml(xml):
    if xml.tag != 'raw':
        raise zeit.cms.interfaces.ValidationError(_('The root element must be <raw>.'))
    return True


class IRawXML(IBlock):
    xml = zeit.cms.content.field.XMLTree(
        title=_('XML source'), tidy_input=True, constraint=validate_rawxml
    )


class IRawText(IBlock, zeit.content.modules.interfaces.IRawText):
    pass


class IEmbed(IBlock, zeit.content.modules.interfaces.IEmbed):
    pass


class AnimationObjectSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'animation'
    check_interfaces = (IAnimation,)


class IAnimation(IBlock):
    animation = zope.schema.Choice(
        title=_('URL of animation'),
        source=AnimationObjectSource(),
        required=True,
    )


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


class ICitation(IBlock):
    text = zope.schema.Text(title=_('Citation'))

    attribution = zope.schema.TextLine(title=_('Attribution'), required=False)

    url = zope.schema.URI(title=_('URL'), required=False)

    layout = zope.schema.Choice(
        title=_('Layout'), source=CITATION_LAYOUT_SOURCE, default='default', required=False
    )


class ICitationComment(IBlock):
    text = zope.schema.Text(title=_('Citation Comment'))

    url = zope.schema.URI(title=_('URL'), required=False)

    layout = zope.schema.Choice(
        title=_('Layout'), source=CITATIONCOMMENT_LAYOUT_SOURCE, default='default', required=False
    )


class LiveblogVersions(zeit.cms.content.sources.SimpleFixedValueSource):
    values = collections.OrderedDict(
        [
            ('3', '3'),
        ]
    )


class ILiveblog(IBlock):
    blog_id = zope.schema.TextLine(title=_('Liveblog id'))

    version = zope.schema.Choice(
        title=_('Liveblog version'), source=LiveblogVersions(), default='3', required=False
    )

    collapse_preceding_content = zope.schema.Bool(
        title=_('Collapse preceding content'), default=True, required=False
    )


class ITickarooLiveblog(IBlock, zeit.content.modules.interfaces.ITickarooLiveblog):
    pass


class ICardstack(IBlock):
    card_id = zope.schema.TextLine(title=_('Cardstack id'))
    is_advertorial = zope.schema.Bool(title=_('Advertorial?'), default=False)


class IQuiz(IBlock, zeit.content.modules.interfaces.IQuiz):
    pass


class IBox(IBlock):
    """
    This box is a first step to generalizing other boxes
    (infobox, portraitbox...). Another field, the body, should be added, which
    has the ability to contain other content, like additional images.
    """

    supertitle = zope.schema.TextLine(
        title=_('Supertitle'),
        description=_('Please take care of capitalisation.'),
        required=False,
        max_length=70,
    )

    title = zope.schema.TextLine(title=_('Title'), required=False, max_length=70)

    subtitle = zope.schema.Text(title=_('Subtitle'), required=False)

    layout = zope.schema.Choice(title=_('Layout'), required=True, source=BOX_LAYOUT_SOURCE)


JOBTICKER_SOURCE = zeit.content.modules.jobticker.FeedSource(
    zeit.content.article.interfaces.IArticle
)


class IJobTicker(IBlock, zeit.content.modules.interfaces.IJobTicker):
    feed = zope.schema.Choice(title=_('Jobbox ticker'), required=True, source=JOBTICKER_SOURCE)


class IMail(IBlock, zeit.content.modules.interfaces.IMail):
    pass


class IBreakingNewsBody(zope.interface.Interface):
    text = zope.schema.Text(
        title=_('Article body'), default=_('breaking-news-more-shortly'), required=False
    )


class AdplaceTileSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = collections.OrderedDict(
        [
            ('desktop_3', 'Desktop: 3'),
            ('desktop_4', 'Desktop: 4'),
            ('desktop_5', 'Desktop: 5'),
            ('desktop_8', 'Desktop: 8'),
            ('desktop_41', 'Desktop: 41'),
            ('desktop_42', 'Desktop: 42'),
            ('desktop_43', 'Desktop: 43'),
            ('mobile_1', 'Mobile: 1'),
            ('mobile_3', 'Mobile: 3'),
            ('mobile_4', 'Mobile: 4'),
            ('mobile_41', 'Mobile: 41'),
            ('mobile_42', 'Mobile: 42'),
            ('mobile_43', 'Mobile: 43'),
            ('ctm', 'Content Marketing Teaser Mobil / Desktop'),
            ('special', 'Desktop: 3 und Mobil: 1'),
        ]
    )


class IAdplace(IBlock):
    tile = zope.schema.Choice(title=_('Adplace Tile'), required=True, source=AdplaceTileSource())


class IPuzzle(zope.interface.Interface):
    """A puzzle type"""

    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    multiple = zope.interface.Attribute('Has multiple episodes')


class Puzzle(zeit.cms.content.sources.AllowedBase):
    def __init__(self, id, title, multiple):
        super().__init__(id, title, None)
        self.multiple = multiple


class PuzzleSource(
    zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.SimpleContextualXMLSource
):
    product_configuration = 'zeit.content.article'
    config_url = 'puzzleforms-source'
    default_filename = 'puzzleforms.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            puzzle = Puzzle(node.get('id'), node.text.strip(), node.get('multiple') == 'true')
            result[puzzle.id] = puzzle
        return result

    def getTitle(self, context, value):
        return value.title


PUZZLE_SOURCE = PuzzleSource()


class IPuzzleForm(IBlock):
    puzzle_type = zope.schema.Choice(title=_('Puzzle'), required=True, source=PUZZLE_SOURCE)

    year = zope.schema.Int(
        title=_('Year'),
        min=datetime.date.today().year,
        default=datetime.date.today().year,
    )


class PreconfiguredQuerySource(zeit.contentquery.interfaces.TopicpageFilterSource):
    product_configuration = 'zeit.content.article'
    default_filename = 'topicpage-esqueries.json'

    def getQuery(self, value):
        try:
            return self.json_data()[value].get('query', value)
        except Exception:
            return None


class TopicboxTypeSource(zeit.cms.content.sources.SimpleDictSource):
    values = collections.OrderedDict(
        [
            ('manual', _('manual')),
            ('centerpage', _('centerpage')),
            ('topicpage', _('topicpage')),
            ('elasticsearch-query', _('elasticsearch-query')),
            ('related-api', _('related-api')),
            ('preconfigured-query', _('preconfigured-query')),
        ]
    )

    def getToken(self, value):
        # JS needs to use these values, don't MD5 them.
        return value


class TopicReferenceSource(zeit.cms.content.contentsource.CMSContentSource):
    def __init__(self, allow_cp=False):
        self.allow_cp = allow_cp
        self._allowed_interfaces = (
            zeit.content.article.interfaces.IArticle,
            zeit.content.gallery.interfaces.IGallery,
            zeit.content.video.interfaces.IVideo,
            zeit.content.link.interfaces.ILink,
        )

    @property
    def check_interfaces(self):
        if not self.allow_cp:
            return self._allowed_interfaces
        return self._allowed_interfaces + (zeit.content.cp.interfaces.ICenterPage,)


class ITopicbox(IBlock, zeit.contentquery.interfaces.IConfiguration):
    """
    Element which references other Articles
    """

    supertitle = zope.schema.TextLine(
        title=_('Supertitle'), description=_('Please take care of capitalisation.'), max_length=30
    )

    title = zope.schema.TextLine(title=_('Title'), max_length=30)

    link = zope.schema.URI(
        title=_('Link'), required=False, constraint=zeit.cms.interfaces.valid_link_target
    )

    link_text = zope.schema.TextLine(title=_('Linktext'), required=False, max_length=30)

    automatic_type = zope.schema.Choice(
        title=_('Automatic type'), source=TopicboxTypeSource(), required=True, default='centerpage'
    )

    first_reference = zope.schema.Choice(
        title=_('Reference'),
        description=_('Drag article/cp/link here'),
        source=TopicReferenceSource(allow_cp=True),
        required=False,
    )

    second_reference = zope.schema.Choice(
        title=_('Reference'),
        description=_('Drag article/link here'),
        source=TopicReferenceSource(),
        required=False,
    )

    third_reference = zope.schema.Choice(
        title=_('Reference'),
        description=_('Drag article/link here'),
        source=TopicReferenceSource(),
        required=False,
    )

    preconfigured_query = zope.schema.Choice(
        title=_('Filter'), source=PreconfiguredQuerySource(), required=False
    )

    def values():
        """
        Iterable of ICMSContent
        """


class INewsletterSignup(IBlock, zeit.content.modules.interfaces.INewsletterSignup):
    pass


class IRecipeList(IBlock, zeit.content.modules.interfaces.IRecipeList):
    pass


class IIngredientDice(IBlock):
    """A simple block without any customisation.
    If something like article-extras would exist this should be one.
    """

    pass
