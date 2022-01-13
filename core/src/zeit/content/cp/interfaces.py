from zeit.cms.i18n import MessageFactory as _
from zeit.contentquery.interfaces import IConfiguration
import collections
import fractions
import json
import logging
import zc.sourcefactory.contextual
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.tagging.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.field
import zeit.content.cp.layout
import zeit.content.cp.source
import zeit.content.image.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.jobticker
import zeit.content.video.interfaces
import zeit.edit.interfaces
import zeit.retresco.interfaces
import zeit.seo.interfaces
import zope.i18n
import zope.interface


log = logging.getLogger(__name__)


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.cp'
TEASER_ID_NAMESPACE = 'http://teaser.vivi.zeit.de/'


zope.security.checker.BasicTypes[fractions.Fraction] = (
    zope.security.checker.NoProxy)


class ITopicLinks(zope.interface.Interface):

    topiclink_label_1 = zope.schema.TextLine(
        title=_('Label for topiclink #1'),
        required=False)

    topiclink_label_2 = zope.schema.TextLine(
        title=_('Label for topiclink #2'),
        required=False)

    topiclink_label_3 = zope.schema.TextLine(
        title=_('Label for topiclink #3'),
        required=False)

    topiclink_url_1 = zope.schema.TextLine(
        title=_('URL for topiclink #1'),
        required=False)

    topiclink_url_2 = zope.schema.TextLine(
        title=_('URL for topiclink #2'),
        required=False)

    topiclink_url_3 = zope.schema.TextLine(
        title=_('URL for topiclink #3'),
        required=False)


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zeit.edit.interfaces.IContainer,
                  ITopicLinks,
                  zeit.retresco.interfaces.ISkipEnrich):

    type = zope.schema.Choice(
        title=_('CP type'),
        source=zeit.content.cp.source.CPTypeSource(),
        default='centerpage')

    header_image = zope.schema.Choice(
        title=_('Header image'),
        required=False,
        source=zeit.content.image.interfaces.imageSource)

    topiclink_title = zope.schema.TextLine(
        title=_('Name for topiclinks'),
        required=False)

    og_title = zope.schema.TextLine(
        title=_('Titel'),
        required=False)

    og_description = zope.schema.TextLine(
        title=_('Description'),
        required=False)

    og_image = zope.schema.TextLine(
        title=_('Image'),
        required=False)

    keywords = zeit.cms.tagging.interfaces.Keywords(
        required=False,
        default=())

    def __getitem__(area_key):
        """Return IArea for given key.

        area_key references <foo area="area_key"

        NOTE: currently the only valid keys are

            - lead
            - informatives
            - mosaic

        """

    def updateMetadata(content):
        """Update the metadata of the given content object."""

    cache = zope.interface.Attribute("""\
        Returns a (transaction bound) cache, which can be used for various
        things like rendered areas, teaser contents, query objects etc.""")

    cached_areas = zope.interface.Attribute("""\
        Cached list of all IArea objects; IContentQuery uses this instead of
        iterating over body/regions/values, for performance reasons.""")


class IStoryStream(ICenterPage):
    """CP with ``type``=='storystream'.

    We're pretending this is a separate content type by providing its own
    AddForm. (XXX Maybe convert to an actual content type that inherits from
    Centerpage?)
    """


IStoryStream.setTaggedValue(
    'zeit.cms.addform', 'zeit.content.cp.AddStoryStream')
IStoryStream.setTaggedValue('zeit.cms.title', _('Add storystream'))


class ISitemap(ICenterPage):
    """CP with ``type``=='sitemap'.

    This interface is applied manually.
    """


class ISearchpage(ICenterPage):
    """CP with ``type``=='search'.

    This interface is applied manually.
    """


class IElement(zeit.edit.interfaces.IElement):
    """generic element, but CP-specific"""

    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)

    visible_mobile = zope.schema.Bool(
        title=_('Visible on mobile'),
        default=True)


class IBody(zeit.edit.interfaces.IArea, IElement):
    """Container of the CenterPage that actually contains the children."""


class IReadRegion(zeit.edit.interfaces.IReadContainer):

    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    __name__ = zope.schema.TextLine(
        title=_("Name"),
        required=True)

    # XXX We need to repeat these from IElement for security declarations.
    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)
    visible_mobile = zope.schema.Bool(
        title=_('Visible on mobile'),
        default=True)

    kind = zope.schema.TextLine(
        title=_("Kind"))

    kind_title = zope.schema.TextLine(
        title=_("Kind Title"))


class IWriteRegion(zeit.edit.interfaces.IWriteContainer):
    pass


class IRegion(
        IReadRegion,
        IWriteRegion,
        zeit.edit.interfaces.IContainer,
        IElement):
    """Abstract layer above IArea."""

    zope.interface.invariant(zeit.edit.interfaces.unique_name_invariant)


class BelowAreaSource(
        zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """All IAreas of this CenterPage below the current one."""

    def getValues(self, context):
        cp = zeit.content.cp.interfaces.ICenterPage(context)
        areas = []
        below = False
        for region in cp.values():
            for area in region.values():
                if area == context:
                    below = True
                    continue
                if below:
                    areas.append(area)
        return areas

    def getTitle(self, context, value):
        # XXX Hard-code language, since we don't have a request here.
        return zope.i18n.translate(
            _("${kind} area ${title}", mapping=dict(
                kind=value.kind, title=value.title or _("no title"))),
            target_language='de')

    def getToken(self, context, value):
        return value.__name__


class AutomaticTypeSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict([
        ('centerpage', _('automatic-area-type-centerpage')),
        ('custom', _('automatic-area-type-custom')),
        ('topicpage', _('automatic-area-type-topicpage')),
        ('related-topics', _('automatic-area-type-related-topics')),
        ('query', _('automatic-area-type-query')),
        ('elasticsearch-query', _('automatic-area-type-elasticsearch-query')),
        ('reach', _('automatic-area-type-reach')),
        ('rss-feed', _('automatic-area-type-rss-feed'))
    ])

    def getToken(self, value):
        # JS needs to use these values, don't MD5 them.
        return value


def automatic_area_can_read_teasers_automatically(data):
    if data.automatic_type == 'centerpage' and data.referenced_cp:
        return True

    if data.automatic_type == 'custom' and data.query:
        return True

    if data.automatic_type == 'topicpage' and data.referenced_topicpage:
        return True

    if data.automatic_type == 'related-topics' and data.related_topicpage:
        return True

    if data.automatic_type == 'query' and data.raw_query:
        return True

    if (data.automatic_type == 'elasticsearch-query' and
            data.elasticsearch_raw_query):
        return True

    if (data.automatic_type == 'rss-feed' and
            data.rss_feed):
        return True

    if (data.automatic_type == 'reach' and data.reach_service):
        return True
    return False


class AreaColorThemesSource(zeit.cms.content.sources.XMLSource):

    attribute = 'name'
    config_url = 'area-color-themes-source'
    default_filename = 'area-color-themes.xml'
    product_configuration = 'zeit.content.cp'
    title_xpath = '/color-themes/theme'

    def isAvailable(self, node, context):
        cp = zeit.content.cp.interfaces.ICenterPage(context, None)
        return super().isAvailable(node, cp)


AREA_COLOR_THEMES_SOURCE = AreaColorThemesSource()


class IReadArea(
        zeit.edit.interfaces.IReadContainer,
        ITopicLinks,
        IConfiguration):

    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)

    # XXX We need to repeat this from IElement for security declarations.
    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)

    kind = zope.schema.TextLine(
        title=_("Kind"),
        description=_("Used internally for rendering on Friedbert"),
        default='solo')

    kind_title = zope.interface.Attribute(
        "Translation of kind to a human friendly information")

    supertitle = zope.schema.TextLine(
        title=_("Supertitle"),
        required=False)

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    read_more = zope.schema.TextLine(
        title=_("Read more"),
        required=False)

    read_more_url = zope.schema.TextLine(
        title=_("Read more URL"),
        required=False)

    image = zope.schema.Choice(
        title=_('Image'),
        description=_("Drag an image group here"),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource)

    # XXX We need to repeat this from IElement for security declarations.
    visible_mobile = zope.schema.Bool(
        title=_('Visible on mobile'),
        default=True)

    block_max = zope.schema.Int(
        title=_("Maximum block count"),
        required=False)

    overflow_into = zope.schema.Choice(
        title=_("Overflow into"),
        source=BelowAreaSource(),
        required=False)

    apply_teaser_layouts_automatically = zope.schema.Bool(
        title=_('Apply teaser layouts automatically?'),
        required=False,
        default=False)

    first_teaser_layout = zope.schema.Choice(
        title=_('First teaser layout'),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource(),
        required=False)

    default_teaser_layout = zope.interface.Attribute(
        'Default layout for teaser lists inside this area')

    require_lead_candidates = zope.schema.Bool(
        title=_('Require lead candidates when auto filling?'),
        default=True)

    automatic = zope.schema.Bool(
        title=_('automatic'),
        default=False)
    automatic.__doc__ = """If True, IRenderedArea.values() will populate
    any IAutomaticTeaserBlock with content, as specified by automatic_type.
    """
    # XXX really ugly styling hack
    automatic.setTaggedValue('placeholder', ' ')

    automatic_type = zope.schema.Choice(
        title=_('Automatic type'),
        source=AutomaticTypeSource(),
        required=True)

    area_color_theme = zope.schema.Choice(
        title=_("Area color theme (ze.tt only)"),
        source=AREA_COLOR_THEMES_SOURCE,
        required=False)

    @zope.interface.invariant
    def automatic_type_required_arguments(data):
        if (data.automatic and
                not automatic_area_can_read_teasers_automatically(data)):
            if data.automatic_type == 'centerpage':
                error_message = _(
                    'Automatic area with teaser from centerpage '
                    'requires a referenced centerpage.')
            if data.automatic_type == 'custom':
                error_message = _(
                    'Automatic area with teaser from custom query '
                    'requires a query condition.')
            if data.automatic_type == 'topicpage':
                error_message = _(
                    'Automatic area with teaser from TMS topicpage '
                    'requires a topicpage ID.')
            if data.automatic_type == 'elasticsearch-query':
                error_message = _(
                    'Automatic area with teaser from elasticsearch query '
                    'requires a raw query.')
            if data.automatic_type == 'rss-feed':
                error_message = _(
                    'Automatic area with rss-feed requires a given feed')
            if data.automatic_type == 'related-topics':
                error_message = _(
                    'Automatic area with related-topics requires a given'
                    ' topicpage')
            if data.automatic_type == 'reach':
                error_message = _(
                    'Automatic area with teasers from reach require a given'
                    ' kind')
            raise zeit.cms.interfaces.ValidationError(error_message)
        return True

    @zope.interface.invariant
    def elasticsearch_valid_json_query(data):
        """Check the es raw query is plausible elasticsearch DSL"""
        if data.automatic_type == 'elasticsearch-query' and (
                data.elasticsearch_raw_query):
            try:
                query = json.loads(data.elasticsearch_raw_query)
                if 'query' not in query:
                    raise ValueError('Top-level key "query" is required.')
            except Exception as err:
                raise zeit.cms.interfaces.ValidationError(
                    _('Elasticsearch raw query is malformed: %s' % err))
        return True

    def adjust_auto_blocks_to_count():
        """Updates number of teaser in AutoPilot, if AutoPilot is enabled"""


class IWriteArea(zeit.edit.interfaces.IWriteContainer):
    pass


# Must split read / write for security declarations for IArea.
class IArea(IReadArea, IWriteArea, zeit.edit.interfaces.IArea, IElement):
    """An area contains blocks."""

    zope.interface.invariant(zeit.edit.interfaces.unique_name_invariant)


class IRenderedArea(IArea):
    """Overrides values() to evaluate any automatic settings.
    """

    start = zope.interface.Attribute(
        'Offset the IContentQuery result by this many content objects. '
        'This is an extension point for zeit.web to do pagination.')


class ITeaseredContent(zope.interface.common.sequence.IReadSequence):
    """Returns an iterable content objects in a CenterPage, that are referenced
    by ITeaserBlocks, in the same order they appear in the CenterPage.
    """


class IBlock(IElement, zeit.edit.interfaces.IBlock):

    supertitle = zope.schema.TextLine(
        title=_("Supertitle"),
        required=False)
    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)
    type_title = zope.interface.Attribute(
        "Translation of type to a human friendly information")
    volatile = zope.schema.Bool(
        title=_("Whether block can be removed by automation, e.g. AutoPilot"),
        default=False)

    # BBB needed by zeit.web for legacy/zmo content only
    read_more = zope.schema.TextLine(
        title=_("Read more"),
        required=False)
    read_more_url = zope.schema.TextLine(
        title=_("Read more URL"),
        required=False)
    background_color = zope.schema.TextLine(
        title=_("Background color (ZMO only)"),
        required=False,
        max_length=6, constraint=zeit.cms.content.interfaces.hex_literal)


class IUnknownBlock(zeit.edit.interfaces.IUnknownBlock, IBlock):
    pass


#
# Teaser block (aka teaser list)
#


# ObjectPathAttributeProperty talks directly to the field,
# so it has no access to the token machinery, thus no conversion
# from/to string happens there -- so we need to do that explicitly.
class IntChoice(zope.schema.Choice):

    def fromUnicode(self, value):
        try:
            value = int(value)
        except Exception:
            pass
        return super().fromUnicode(value)


class IReadTeaserBlock(IBlock, zeit.cms.syndication.interfaces.IReadFeed):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource())

    force_mobile_image = zope.schema.Bool(
        title=_('Force image on mobile'),
        default=True)


class IWriteTeaserBlock(zeit.cms.syndication.interfaces.IWriteFeed):

    def update(other):
        """Copy content and properties from another ITeaserBlock."""


class ITeaserBlock(IReadTeaserBlock, IWriteTeaserBlock):
    """A list of teasers."""


class IReadLocalTeaserBlock(IReadTeaserBlock):

    teaserSupertitle = zope.schema.TextLine(
        title=_('Teaser kicker'),
        required=False)

    teaserTitle = zope.schema.TextLine(
        title=_("Teaser title"),
        required=False)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False)

    # Implementing a separate IImages adapter for ILocalTeaserBlock seems way
    # more effort than it's worth, so we include the two fields here instead.
    # But we don't inherit from IImages, since zeit.web would not be able to
    # override that, and it needs to apply IImages to the teasered content
    # object, instead of the module.
    image = zeit.content.image.interfaces.IImages['image']
    fill_color = zeit.content.image.interfaces.IImages['fill_color']


class IWriteLocalTeaserBlock(IWriteTeaserBlock):
    pass


class ILocalTeaserBlock(
        IReadLocalTeaserBlock,
        IWriteLocalTeaserBlock,
        ITeaserBlock):
    """Teaser module that allows overriding title/text/image"""


class IReadAutomaticTeaserBlock(IReadTeaserBlock):

    force_mobile_image = zope.schema.Bool(
        title=_('Force image on mobile'),
        required=False,
        default=False)


class IWriteAutomaticTeaserBlock(IWriteTeaserBlock):

    def change_layout(layout):
        """Temporarily change the layout (for the duration of one area.values()
        evaluation)."""

    def materialize():
        """Convert this block to a normal ITeaserBlock, filled with the
        current automatic content.
        """


class IAutomaticTeaserBlock(IReadAutomaticTeaserBlock,
                            IWriteAutomaticTeaserBlock,
                            ITeaserBlock):
    pass


def validate_xml_block(xml):
    if xml.tag != 'container':
        raise zeit.cms.interfaces.ValidationError(
            _("The root element must be <container>."))
    if xml.get('{http://namespaces.zeit.de/CMS/cp}type') != 'xml':
        raise zeit.cms.interfaces.ValidationError(
            _("cp:type must be 'xml'."))
    if not xml.get('{http://namespaces.zeit.de/CMS/cp}__name__'):
        raise zeit.cms.interfaces.ValidationError(
            _("No or empty cp:__name__ attribute."))
    return True


class IXMLBlock(IBlock):
    """A block containing raw XML."""

    xml = zeit.cms.content.field.XMLTree(
        title=_("XML Source"),
        constraint=validate_xml_block,
        tidy_input=True)


class IPlaylistBlock(IBlock):
    """A block which contains the link to a video playlist."""

    referenced_playlist = zope.schema.Choice(
        title=_("Playlist"),
        source=zeit.content.video.interfaces.PlaylistSource())


class ICPExtraBlock(IBlock):
    """Block which contains a cp_extra."""

    cpextra = zope.schema.Choice(
        title=_('CP Extra Id'),
        source=zeit.content.cp.source.CPExtraSource())


class ITeaser(zeit.cms.content.interfaces.ICommonMetadata,
              zeit.cms.content.interfaces.IXMLContent):
    """A standalone teaser object which references the article."""

    original_content = zope.schema.Choice(
        title='The referenced article.',
        source=zeit.cms.content.contentsource.cmsContentSource)


class IQuizBlock(zeit.content.modules.interfaces.IQuiz, IBlock):
    pass


class ILeadTime(zope.interface.Interface):

    start = zope.schema.Datetime(title=_('From'))
    end = zope.schema.Datetime(title=_('To'))


class ILeadTimeCP(zope.interface.Interface):
    """Marks a CenterPage: store ILeadTime information on articles
    that are referenced on this CP.
    """


class ILeadTimeWorklist(zope.interface.Interface):

    previous_leader = zope.schema.Choice(
        source=zeit.cms.content.contentsource.CMSContentSource())


class IRenderedXML(zope.interface.Interface):
    """Recursively converts a CenterPage to an lxml tree."""


class IRawTextBlock(zeit.content.modules.interfaces.IRawText, IBlock):
    pass


class IHeaderImageBlock(IBlock):

    image = zope.schema.Choice(
        title=_('Image'),
        description=_("Drag an image group here"),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource)
    animate = zope.schema.Bool(
        title=_('Animate'),
        default=False)


class AlignmentSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict((
        ('left', _('left')),
        ('center', _('center')),
        ('right', _('right')),
    ))


class IMarkupBlock(IBlock):

    text = zope.schema.Text(
        title=_('Contents'),
        description=_('Use Markdown'),
        required=True)
    markdown = zope.interface.Attribute('Text in markdown format')
    alignment = zope.schema.Choice(
        title=_('Alignment'),
        description=_('Choose alignment'),
        source=AlignmentSource(),
        default='left')


class CardstackColorSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict((
        (color, color) for color in [
            '#D8D8D8',
            '#5E534F',
            '#E4DED8',
            '#69696C',
            '#FF7783',
            '#7C0E14',
            '#6FA6B9',
            '#085064',
            '#57C494',
            '#1E6847']
    ))


class ICardstackBlock(IBlock):

    card_id = zope.schema.TextLine(
        title=_('Cardstack id'))

    is_advertorial = zope.schema.Bool(
        title=_('Advertorial?'),
        default=False)

    cardstack_background_color = zope.schema.Choice(
        title=_('Background color'),
        description=_('Choose a background color'),
        source=CardstackColorSource()
    )


JOBTICKER_SOURCE = zeit.content.modules.jobticker.FeedSource(
    ICenterPage)


class IJobTickerBlock(zeit.content.modules.interfaces.IJobTicker, IBlock):
    """The Jobticker block with a specific feed specified in source."""

    feed = zope.schema.Choice(
        title=_('Jobbox Ticker'),
        required=True,
        source=JOBTICKER_SOURCE)


class IPodcastBlock(IBlock, zeit.content.modules.interfaces.PodcastBase):
    """The Podcast block with a reference to a podcast."""
    pass


class IMailBlock(zeit.content.modules.interfaces.IMail, IBlock):
    pass


class INewsletterSignupBlock(
        zeit.content.modules.interfaces.INewsletterSignup, IBlock):
    pass


# BBB We don't need this anymore, but existing content still has it.
class ICP2015(ICenterPage):
    """Marker interfaces for CPs edited by the current CP-Editor (master)."""


class ICpSEO(zeit.seo.interfaces.ISEO):
    enable_rss_tracking_parameter = zope.schema.Bool(
        title=_('Enable RSS Tracking-Parameter'),
        required=False)
