from zeit.cms.application import CONFIG_CACHE
from zeit.cms.i18n import MessageFactory as _
import collections
import fractions
import json
import logging
import urllib2
import urlparse
import zc.sourcefactory.contextual
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.tagging.interfaces
import zeit.content.cp.layout
import zeit.content.cp.source
import zeit.content.image.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.jobticker
import zeit.content.video.interfaces
import zeit.edit.interfaces
import zope.i18n
import zope.interface


log = logging.getLogger(__name__)


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.cp'
TEASER_ID_NAMESPACE = 'http://teaser.vivi.zeit.de/'


zope.security.checker.BasicTypes[fractions.Fraction] = (
    zope.security.checker.NoProxy)


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zeit.edit.interfaces.IContainer):

    type = zope.schema.Choice(
        title=_('CP type'),
        source=zeit.content.cp.source.CPTypeSource(),
        default=u'centerpage')

    header_image = zope.schema.Choice(
        title=_('Header image'),
        required=False,
        source=zeit.content.image.interfaces.imageSource)

    topiclink_title = zope.schema.TextLine(
        title=_('Name for topiclinks'),
        required=False)

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

    def content_areas():
        """Returns a (cached) list of content objects contained in any
        ITeaserBlock module on the page."""

    def teasered_content_above(area):
        """Returns set of content objects contained in any
        ITeaserBlock module above the given area (IRenderedArea or manual)."""

    def manual_content_below(area):
        """Returns set of content objects contained in any
        ITeaserBlock module below the given area (IRenderedArea is *not*
        executed).
        """


class ICP2009(ICenterPage):
    """Marker interfaces for CPs edited by the old 2.x CP-Editor branch."""


class ICP2015(ICenterPage):
    """Marker interfaces for CPs edited by the current CP-Editor (master)."""


class IStoryStream(ICP2015):
    """CP with ``type``=='storystream'.

    We're pretending this is a separate content type by providing its own
    AddForm. (XXX Maybe convert to an actual content type that inherits from
    Centerpage?)
    """
IStoryStream.setTaggedValue(
    'zeit.cms.addform', 'zeit.content.cp.AddStoryStream')
IStoryStream.setTaggedValue(
    'zeit.cms.title', _('Add storystream'))


class ISitemap(ICP2015):
    """CP with ``type``=='sitemap'.

    This interface is applied manually.
    """


class ISearchpage(ICP2015):
    """CP with ``type``=='search'.

    This interface is applied manually.
    """


class IBody(zeit.edit.interfaces.IArea):
    """Container of the CenterPage that actually contains the children."""


class IElement(zeit.edit.interfaces.IElement):
    """generic element, but CP-specific"""

    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)

    visible_mobile = zope.schema.Bool(
        title=_('Visible on mobile'),
        default=True)


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


class AutomaticTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):

    prefix = 'automatic-area-type-{}'

    values = (
        u'centerpage', u'channel', u'topicpage', u'query',
        u'elasticsearch-query')

    def __init__(self):
        self.titles = dict((x, _(self.prefix.format(x))) for x in self.values)

    def getToken(self, value):
        # JS needs to use these values, don't MD5 them.
        return value


class SimpleDictSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = collections.OrderedDict()

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values.get(value, value)


class QuerySortOrderSource(SimpleDictSource):

    values = collections.OrderedDict((
        ('payload.workflow.date_last_published_semantic:desc',
         _('query-sort-order-last-published-semantic')),
        ('payload.document.last-semantic-change:desc',
         _('query-sort-order-last-semantic-change')),
        ('payload.document.date_first_released:desc',
         _('query-sort-order-first-released')),
    ))


class TopicpageFilterSource(zc.sourcefactory.basic.BasicSourceFactory):

    @CONFIG_CACHE.cache_on_arguments()
    def json_data(self):
        url = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp').get('topicpage-filter-source')
        try:
            return json.load(urllib2.urlopen(url))
        except Exception:
            log.warning(
                'TopicpageFilterSource could not parse %s', url, exc_info=True)
            return []

    def getValues(self):
        return [x.keys()[0] for x in self.json_data()]

    def getTitle(self, value):
        return value

    def getToken(self, value):
        return value


def automatic_area_can_read_teasers_automatically(data):
    if data.automatic_type == 'centerpage' and data.referenced_cp:
        return True

    if data.automatic_type == 'channel' and data.query:
        return True

    if data.automatic_type == 'topicpage' and data.referenced_topicpage:
        return True

    if data.automatic_type == 'query' and data.raw_query:
        return True

    if (data.automatic_type == 'elasticsearch-query' and
            data.elasticsearch_raw_query):
        return True

    return False


class IReadArea(zeit.edit.interfaces.IReadContainer):

    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)

    # XXX We need to repeat this from IElement for security declarations.
    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)

    kind = zope.schema.TextLine(
        title=_("Kind"),
        description=_("Used internally for rendering on Friedbert"))

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

    automatic_type = zope.schema.Choice(
        title=_('automatic-area-type'),
        source=AutomaticTypeSource(),
        required=True)
    automatic_type.__doc__ = """Determines from where IRenderedArea retrieves
    content objects. Will look up a utility of that name for IContentQuery.
    """

    # XXX Rename to make clear that this setting only applies to AutoPilot.
    count = zope.schema.Int(title=_('Amount of teasers'), default=15)

    referenced_cp = zope.schema.Choice(
        title=_('Get teasers from CenterPage'),
        source=zeit.content.cp.source.centerPageSource,
        required=False)

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    # XXX Rename more specifically (TMS-227)
    query = zope.schema.Tuple(
        title=_('Channel Query'),
        value_type=zc.form.field.Combination(
            (zope.schema.Choice(
                title=_('Channel'),
                source=zeit.cms.content.sources.ChannelSource()),
             zope.schema.Choice(
                 title=_('Subchannel'),
                 source=zeit.cms.content.sources.SubChannelSource(),
                 required=False))
        ),
        default=(),
        required=False)
    query_order = zope.schema.Choice(
        title=_('Sort order'),
        source=QuerySortOrderSource(),
        default=u'payload.workflow.date_last_published_semantic:desc',
        required=True)

    referenced_topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage'),
        required=False)

    topicpage_filter = zope.schema.Choice(
        title=_('Topicpage filter'),
        source=TopicpageFilterSource(),
        required=False)

    raw_query = zope.schema.Text(title=_('Raw query'), required=False)
    raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'date-first-released desc',
        required=False)

    elasticsearch_raw_query = zope.schema.Text(
        title=_('Elasticsearch raw query'),
        required=False)
    elasticsearch_raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'payload.document.date_first_released:desc',
        required=False)
    is_complete_query = zope.schema.Bool(
        title=_('Take over complete query body'),
        description=_('Remember to add payload.workflow.published:true'),
        default=False,
        required=False)

    # XXX really ugly styling hack
    automatic.setTaggedValue('placeholder', ' ')
    raw_query.setTaggedValue('placeholder', ' ')

    @zope.interface.invariant
    def automatic_type_required_arguments(data):
        if (data.automatic and
                not automatic_area_can_read_teasers_automatically(data)):
            if data.automatic_type == 'centerpage':
                error_message = _(
                    'Automatic area with teaser from centerpage '
                    'requires a referenced centerpage.')
            if data.automatic_type == 'channel':
                error_message = _(
                    'Automatic area with teaser from solr channel '
                    'requires a channel query.')
            if data.automatic_type == 'topicpage':
                error_message = _(
                    'Automatic area with teaser from TMS topicpage '
                    'requires a topicpage ID.')
            if data.automatic_type == 'query':
                error_message = _(
                    'Automatic area with teaser from solr query '
                    'requires a raw query.')
            if data.automatic_type == 'elasticsearch-query':
                error_message = _(
                    'Automatic area with teaser from elasticsearch query '
                    'requires a raw query.')
            raise zeit.cms.interfaces.ValidationError(error_message)
        return True

    @zope.interface.invariant
    def elasticsearch_valid_json_query(data):
        """Check the es raw query is plausible elasticsearch DSL"""
        if data.automatic_type == 'elasticsearch-query' and (
                data.elasticsearch_raw_query):
            try:
                json.loads(data.elasticsearch_raw_query)
            except (TypeError, ValueError), err:
                raise zeit.cms.interfaces.ValidationError(
                    _('Elasticsearch raw query is malformed: {error}'
                      ).format(error=err.message))
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


class IContentQuery(zope.interface.Interface):
    """Mechanism to retrieve content objects.
    Used to register named adapters for the different IArea.automatic_types.
    """

    total_hits = zope.interface.Attribute(
        'Total number of available results (only available after calling)')

    def __call__(self):
        """Returns list of content objects."""


class ITeaseredContent(zope.interface.common.sequence.IReadSequence):
    """Returns an iterable content objects in a CenterPage, that are referenced
    by ITeaserBlocks, in the same order they appear in the CenterPage.
    """


class ICPFeed(zope.interface.Interface):
    """Feed section of a CenterPage"""

    items = zope.interface.Attribute("tuple of feed items")

    def set_items_and_supress_errors(items):
        pass


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
        except:
            pass
        return super(IntChoice, self).fromUnicode(value)


class TextColorSource(SimpleDictSource):

    values = collections.OrderedDict((
        ('dark', _('Dark (white text)')),
        ('light', _('Light (black text)')),
    ))


class OpacitySource(SimpleDictSource):

    values = collections.OrderedDict((
        ('1', _('opacity-1')),
        ('2', _('opacity-2')),
        ('3', _('opacity-3')),
        ('4', _('opacity-4')),
        ('5', _('opacity-5')),
    ))


class IReadTeaserBlock(IBlock, zeit.cms.syndication.interfaces.IReadFeed):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource())

    force_mobile_image = zope.schema.Bool(
        title=_('Force image on mobile'),
        required=False,
        default=False)

    text_color = zope.schema.Choice(
        title=_('Overlay color'),
        source=TextColorSource(),
        default='dark')

    overlay_level = zope.schema.Choice(
        title=_('Overlay opacity'),
        source=OpacitySource(),
        default='3')


class IWriteTeaserBlock(zeit.cms.syndication.interfaces.IWriteFeed):

    def update_topiclinks():
        """Copy topiclinks of the referenced CP into our XML."""

    def update(other):
        """Copy content and properties from another ITeaserBlock."""


class ITeaserBlock(IReadTeaserBlock, IWriteTeaserBlock):
    """A list of teasers."""


class IReadTeaserBlockColumns(zope.interface.Interface):

    def __getitem__(idx):
        """Return teasers in column ``idx``."""

    def __len__():
        """Return the number of columns.

        (Currently either 1 or 2)

        """


class IWriteTeaserBlockColumns(zope.interface.Interface):
    """Column information for a teaser block."""

    def __setitem__(idx, amount):
        """Set teasers in column ``idx``.

        NOTE: The only valid value of ``idx`` is 0 at the moment.

        """


class ITeaserBlockColumns(IReadTeaserBlockColumns, IWriteTeaserBlockColumns):
    """Column information for a teaser block."""


class IReadAutomaticTeaserBlock(IReadTeaserBlock):
    pass


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


def valid_feed_url(uri):
    zope.schema.URI().fromUnicode(uri)  # May raise InvalidURI
    if urlparse.urlparse(uri).scheme in ('http', 'https', 'file'):
        return True
    # NOTE: we hide the fact that we support (some) file urls.
    raise zeit.cms.interfaces.ValidationError(
        _('Only http and https are supported.'))


class ICPExtraBlock(IBlock):
    """Block which contains a cp_extra."""

    cpextra = zope.schema.Choice(
        title=_('CP Extra Id'),
        source=zeit.content.cp.source.CPExtraSource())


class ITeaser(zeit.cms.content.interfaces.ICommonMetadata,
              zeit.cms.content.interfaces.IXMLContent):
    """A standalone teaser object which references the article."""

    original_content = zope.schema.Choice(
        title=u'The referenced article.',
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


class AlignmentSource(SimpleDictSource):

    values = collections.OrderedDict((
        ('left', _('left')),
        ('center', _('center')),
        ('right', _('right')),
    ))


class IMarkupBlock(IBlock):

    text = zope.schema.Text(
        title=_('Contents'),
        description=_('Use Markdown'),
        required=False)
    alignment = zope.schema.Choice(
        title=_('Alignment'),
        description=_('Choose alignment'),
        source=AlignmentSource(),
        default='left')


class ICardstackBlock(IBlock):

    card_id = zope.schema.TextLine(
        title=_('Cardstack id'))
    is_advertorial = zope.schema.Bool(
        title=_('Advertorial?'),
        default=False)


JOBTICKER_SOURCE = zeit.content.modules.jobticker.FeedSource(
    ICenterPage)


class IJobTickerBlock(zeit.content.modules.interfaces.IJobTicker, IBlock):
    """The Jobticker block with a specific feed specified in source."""

    feed = zope.schema.Choice(
        title=_('Jobbox Ticker'),
        required=True,
        source=JOBTICKER_SOURCE)


class IPodcastBlock(IBlock):
    """The Podcast block with a reference to a podcast."""

    episode_id = zope.schema.TextLine(
        title=_("Podcast id"))


class IMailBlock(zeit.content.modules.interfaces.IMail, IBlock):
    pass
