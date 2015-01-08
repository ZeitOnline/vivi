from zeit.content.cp.i18n import MessageFactory as _
from zeit.content.cp.layout import ITeaserBlockLayout, IAreaLayout
import urlparse
import zc.form.field
import zeit.cms.content.contentsource
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
import zeit.content.quiz.source
import zeit.edit.interfaces
import zope.interface


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.cp'
TEASER_ID_NAMESPACE = 'http://teaser.vivi.zeit.de/'


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zeit.edit.interfaces.IContainer):
    """A relaunch 09 centerpage."""

    type = zope.schema.Choice(
        title=_('CP type'),
        source=zeit.content.cp.source.CPTypeSource(),
        default=u'centerpage')

    header_image = zope.schema.Choice(
        title=_('Header image'),
        required=False,
        source=zeit.content.image.interfaces.imageSource)

    snapshot = zope.schema.Choice(
        title=_('Snapshot (HP only)'),
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


class CenterPageSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.cp'
    check_interfaces = (ICenterPage,)


centerPageSource = CenterPageSource()


class IBody(zeit.edit.interfaces.IArea):
    """Container of the CenterPage that actually contains the children."""


class IElement(zeit.edit.interfaces.IElement):
    """generic element, but CP-specific"""


class IReadRegion(zeit.edit.interfaces.IReadContainer):

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    __name__ = zope.schema.TextLine(
        title=_("Name"),
        required=True)


class IWriteRegion(zeit.edit.interfaces.IWriteContainer):
    pass


class IRegion(
        IReadRegion,
        IWriteRegion,
        zeit.edit.interfaces.IContainer,
        IElement):
    """Abstract layer above IArea."""

    zope.interface.invariant(zeit.edit.interfaces.unique_name_invariant)


def hex_literal(value):
    try:
        int(value, base=16)
    except ValueError:
        raise zeit.cms.interfaces.ValidationError(_("Invalid hex literal"))
    else:
        return True


class AreaWidthSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'area-width-source'
    attribute = 'id'


class IReadArea(zeit.edit.interfaces.IReadContainer):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.AreaLayoutSource(),
        default=zeit.content.cp.layout.DEFAULT_AREA_LAYOUT)

    width = zope.schema.Choice(
        title=_("Width"),
        source=AreaWidthSource())

    supertitle = zope.schema.TextLine(
        title=_("Supertitle"),
        required=False)

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)


class IWriteArea(zeit.edit.interfaces.IWriteContainer):
    pass


# Must split read / write for security declarations for IArea.
class IArea(IReadArea, IWriteArea, zeit.edit.interfaces.IArea, IElement):
    """An area contains blocks."""

    zope.interface.invariant(zeit.edit.interfaces.unique_name_invariant)


class QueryTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = ['Channel']  # XXX or 'Keyword', see VIV-471


class IAutomaticArea(IArea):

    automatic = zope.schema.Bool(title=_('automatic'))
    count = zope.schema.Int(title=_('Amount of teasers'), default=15)

    query = zope.schema.Tuple(
        title=_('Channel Query'),
        value_type=zc.form.field.Combination(
            (zope.schema.Choice(
                title=_('Channel Query Type'),
                source=QueryTypeSource(), default='Channel'),
             zope.schema.Choice(
                title=_('Channel equals'),
                source=zeit.cms.content.sources.NavigationSource()),
             zope.schema.Choice(
                 title=_('Subchannel'),
                 source=zeit.cms.content.sources.SubChannelSource(),
                 required=False))
        ),
        default=(),
        required=False)

    raw_query = zope.schema.Text(title=_('Raw query'), required=False)

    # XXX really ugly styling hack
    automatic.setTaggedValue('placeholder', ' ')
    raw_query.setTaggedValue('placeholder', ' ')


class ICMSContentIterable(zope.interface.Interface):
    """An iterable object iterating over CMSContent."""

    def __iter__():
        pass


class ICPFeed(zope.interface.Interface):
    """Feed section of a CenterPage"""

    items = zope.interface.Attribute("tuple of feed items")


class IBlock(IElement, zeit.edit.interfaces.IBlock):

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    read_more = zope.schema.TextLine(
        title=_("Read more"),
        required=False)
    read_more_url = zope.schema.TextLine(
        title=_("Read more URL"),
        required=False)

    background_color = zope.schema.TextLine(
        title=_("Background color (ZMO only)"),
        required=False,
        max_length=6, constraint=hex_literal)

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


class AutopilotSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'autopilot'
    check_interfaces = (
        ICenterPage,
        zeit.cms.syndication.interfaces.IFeed,
    )

autopilotSource = AutopilotSource()


class IReadTeaserBlock(IBlock, zeit.cms.syndication.interfaces.IReadFeed):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource())

    referenced_cp = zope.schema.Choice(
        title=_('Get teasers from (autopilot)'),
        source=autopilotSource,
        required=False)

    autopilot = zope.schema.Bool(
        title=_('Autopilot active'))

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    display_amount = IntChoice(
        title=_('Amount of teasers to display'),
        required=False, values=range(1, 6))

    suppress_image_positions = zope.schema.List(
        title=_('Display image at these positions'),
        value_type=zope.schema.Int(),
        required=False)

    visible = zope.schema.Bool(
        title=_('Visible in frontend'),
        default=True)

    @zope.interface.invariant
    def autopilot_requires_referenced_cp(self):
        if self.autopilot and not self.referenced_cp:
            raise zeit.cms.interfaces.ValidationError(
                _("Cannot activate autopilot without referenced centerpage"))
        return True


class IWriteTeaserBlock(zeit.cms.syndication.interfaces.IWriteFeed):

    def update_topiclinks():
        """Copy topiclinks of the referenced CP into our XML."""


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


class IAutomaticTeaserBlock(ITeaserBlock):
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

    referenced_quiz = zope.schema.Choice(
        title=_("Quiz"),
        source=zeit.content.quiz.source.QuizSource())


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
