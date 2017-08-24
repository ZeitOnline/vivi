from zeit.content.cp.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
from zeit.cms.application import CONFIG_CACHE
import collections
import fractions
import urlparse
import zc.form.field
import zc.sourcefactory.contextual
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.tagging.interfaces
import zeit.content.cp.blocks.avsource
import zeit.content.cp.layout
import zeit.content.cp.source
import zeit.content.image.interfaces
import zeit.content.text.interfaces
import zeit.content.video.interfaces
import zeit.edit.interfaces
import zope.app.appsetup.appsetup
import zope.i18n
import zope.interface


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


class CenterPageSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.cp'
    check_interfaces = (ICenterPage,)


centerPageSource = CenterPageSource()


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

    def __init__(self):
        pass  # Don't init self.titles too early

    @cachedproperty
    def values(self):
        config = zope.app.appsetup.appsetup.getConfigContext()
        if not config or config.hasFeature('zeit.retresco.tms'):
            return (u'centerpage', u'channel', u'topicpage', u'query',
                    u'elasticsearch-query')
        else:
            return (u'centerpage', u'channel', u'query')

    @cachedproperty
    def titles(self):
        return dict((x, _(self.prefix.format(x))) for x in self.values)

    def getToken(self, value):
        # JS needs to use these values, don't MD5 them.
        return value


class QueryTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = ['Channel']  # XXX or 'Keyword', see VIV-471


class SimpleDictSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = collections.OrderedDict()

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values.get(value, value)


class QuerySortOrderSource(SimpleDictSource):

    values = collections.OrderedDict((
        ('date-last-published-semantic desc',
         _('query-sort-order-last-published-semantic')),
        ('last-semantic-change desc',
         _('query-sort-order-last-semantic-change')),
        ('date-first-released desc',
         _('query-sort-order-first-released')),
    ))


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

    automatic_type = zope.schema.Choice(
        title=_('automatic-area-type'),
        source=AutomaticTypeSource(),
        required=True)

    # XXX Rename to make clear that this setting only applies to AutoPilot.
    count = zope.schema.Int(title=_('Amount of teasers'), default=15)

    referenced_cp = zope.schema.Choice(
        title=_('Get teasers from CenterPage'),
        source=centerPageSource,
        required=False)

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    query = zope.schema.Tuple(
        title=_('Channel Query'),
        value_type=zc.form.field.Combination(
            (zope.schema.Choice(
                title=_('Channel Query Type'),
                source=QueryTypeSource(), default='Channel'),
             zope.schema.Choice(
                title=_('Channel equals'),
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
        default=u'date-last-published-semantic desc',
        required=True)

    referenced_topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage'),
        required=False)

    raw_query = zope.schema.Text(title=_('Raw query'), required=False)
    raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'date-first-released desc',
        required=False)

    elasticsearch_raw_query = zope.schema.Text(
        title=_('Elasticsearch raw query'), required=False)
    elasticsearch_raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'date_first_released:desc',
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

    def select_modules(*interfaces):
        """Returns only those modules in self.values() that provide any of
        the given interfaces.
        """

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


class IAVBlock(IBlock):
    """ An audio/video block."""

    media_type = zope.schema.Choice(
        title=_("Media type"),
        readonly=True,
        source=zeit.content.cp.blocks.avsource.MediaTypeSource())

    id = zope.schema.TextLine(
        title=_("Media Id"))

    expires = zope.schema.Datetime(
        title=_("Expiration date"),
        required=False)

    format = zope.schema.Choice(
        title=_("Format"),
        source=zeit.content.cp.blocks.avsource.FormatSource())


class IVideoBlock(IAVBlock):

    player = zope.schema.Choice(
        title=_('Player'),
        source=zeit.content.cp.blocks.avsource.PlayerSource(),
        default='vid')


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


class IFeed(zeit.cms.content.interfaces.IXMLContent,
            zeit.cms.interfaces.IAsset):

    url = zope.schema.URI(
        title=_("RSS feed URL (http://...)"),
        constraint=valid_feed_url)

    title = zope.schema.TextLine(
        title=_("Feed title"),
        readonly=True)

    entry_count = zope.schema.Int(
        title=_("Number of entries in feed."""),
        required=False,
        readonly=True)

    last_update = zope.schema.Datetime(
        readonly=True,
        required=False,
        title=_("Last update"""))

    error = zope.schema.TextLine(
        required=False,
        readonly=True,
        title=_("If parsing the feed fails, the error message is stored here.")
    )

    entries = zope.schema.List(
        title=_("Titles of first 15 entries"),
        value_type=zope.schema.Text(),
        readonly=True,
        required=False)

    favicon = zope.schema.URI(
        title=_('Favicon'),
        required=False)

    def fetch_and_convert():
        """Retrieve the feed and convert it to RSS 2.0."""


class IFeedManager(zope.interface.Interface):
    """Global utility providing RSS functionality."""

    def get_feed(url):
        """Get IFeed object for given URL."""

    def refresh_feed(url):
        """Reload the feed object identified by URL."""


class IRSSFolder(zeit.cms.repository.interfaces.IFolder):
    """Marker interface for RSS folder."""


class IRSSBlock(IBlock):
    """ A RSS teaserblock."""

    url = zope.schema.URI(
        title=_("URL of RSS feed (http://...)"),
        constraint=valid_feed_url)

    max_items = zope.schema.Int(
        title=_('Items to show'),
        default=5,
        min=1)

    teaser_image = zope.schema.Choice(
        title=_('Teaser image'),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    feed_icon = zope.schema.Choice(
        title=_('Feed icon'),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    show_supertitle = zope.schema.Bool(
        title=_('Show supertitle'),
        default=True)

    time_format = zope.schema.Choice(
        title=_('Time format'),
        source=zeit.content.cp.source.RSSTimeFormatSource(),
        default=list(zeit.content.cp.source.RSSTimeFormatSource())[0])

    feed = zope.interface.Attribute("The corresponding IFeed object.")


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


class IXMLTeaser(zeit.cms.interfaces.ICMSContent,
                 zeit.cms.content.interfaces.ICommonMetadata):

    free_teaser = zope.schema.Bool(u'Is it a free teaser?')
    original_uniqueId = zope.schema.URI(
        title=u'The unique id of the content referenced by the teaser')
    original_content = zope.interface.Attribute(
        u'The content referenced by the teaser')


class IQuizBlock(IBlock):
    """The Quiz block with a reference to a quiz."""

    quiz_id = zope.schema.TextLine(
        title=_("Quiz id"))


class FullgraphicalScaleSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'scales-fullgraphical-url'
    attribute = 'name'

    def getToken(self, context, value):
        return value


fullgraphical_scale_source = FullgraphicalScaleSource()


class IFullGraphicalBlock(IBlock):
    """The Fullgraphical block with a reference to an object and an image."""

    referenced_object = zope.schema.Choice(
        title=_("Link to"),
        source=zeit.cms.content.contentsource.CMSContentSource())

    image = zope.schema.Choice(
        title=_("Image"),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=fullgraphical_scale_source)


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


class IRawTextBlock(IBlock):

    text_reference = zope.schema.Choice(
        title=_('Raw text reference'),
        required=False,
        source=zeit.content.text.interfaces.textSource)

    text = zope.schema.Text(
        title=_('Raw text'),
        required=False)

    raw_code = zope.interface.Attribute('Raw code from text or text_reference')


class IFrameBlock(IBlock):

    url = zope.schema.URI(
        title=_("URL to include (http://...)"),
        constraint=valid_feed_url)


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


class JobboxTicker(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, available, teaser, landing_url, feed_url):
        super(JobboxTicker, self).__init__(id, title, available)
        self.id = id
        self.teaser = teaser
        self.landing_url = landing_url
        self.feed_url = feed_url

    def __eq__(self, other):
        return super(JobboxTicker, self).__eq__(
            zope.security.proxy.removeSecurityProxy(other))


class JobboxTickerSource(zeit.cms.content.sources.ObjectSource,
                   zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'jobbox-ticker-source'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            jobbox_ticker = JobboxTicker(
                unicode(node.get('id')),
                unicode(node.get('title')),
                zeit.cms.content.sources.unicode_or_none(node.get(
                    'available')),
                unicode(node.get('teaser')),
                unicode(node.get('landing_url')),
                unicode(node.get('feed_url')),
                )
            result[jobbox_ticker.id] = jobbox_ticker
        return result

    def isAvailable(self, value, context):
        cp = ICenterPage(context, None)
        if not cp:
            return False
        return super(JobboxTickerSource, self).isAvailable(value, cp)

JOBBOX_TICKER_SOURCE = JobboxTickerSource()


class IJobboxTickerBlock(IBlock):
    """The Jobbox block with a specific feed specified in source."""

    jobbox_ticker = zope.schema.Choice(
        title=_('Jobbox Ticker'),
        source=JOBBOX_TICKER_SOURCE)

    jobbox_ticker_title = zope.interface.Attribute("Title of the chosen "
                                                   "Jobbox Ticker")


# BBB Strings still used by z.c.cp-2.x, so i18nextract does not lose them.
_("Autopilot")
_("Parquet")
_("Display image at these positions")
_("Get teasers from (autopilot)")
_("Autopilot active")
_("Amount of teasers to display")
_("Cannot activate autopilot without referenced centerpage")
_("Edit teaser layouts")
_("Remaining teaser layout")
_("Cannot enable automatic without count")
_("Automatic contents")
_("Publisher URL")
_("Supertitle URL")
_("Create teaser group")
_("Display teaser group")
_("Save teasers as group")
_("Name of teaser group")
_("Linked teasers")
_("Automatically remove")
_("Teasergroup")
_("Common")
_("No changes")
_("Landing Zone")
_("Variants")
_("Edit in place")
_("Apply for article")
_("Apply only for this page")
