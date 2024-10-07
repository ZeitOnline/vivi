import fractions
import json
import logging

import zope.i18n
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.contentquery.interfaces import IConfiguration
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
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


log = logging.getLogger(__name__)


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.cp'


zope.security.checker.BasicTypes[fractions.Fraction] = zope.security.checker.NoProxy


class ITopicLinks(zope.interface.Interface):
    topiclink_label_1 = zope.schema.TextLine(title=_('Label for topiclink #1'), required=False)

    topiclink_label_2 = zope.schema.TextLine(title=_('Label for topiclink #2'), required=False)

    topiclink_label_3 = zope.schema.TextLine(title=_('Label for topiclink #3'), required=False)

    topiclink_label_4 = zope.schema.TextLine(title=_('Label for topiclink #4'), required=False)

    topiclink_label_5 = zope.schema.TextLine(title=_('Label for topiclink #5'), required=False)

    topiclink_url_1 = zope.schema.URI(
        title=_('URL for topiclink #1'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    topiclink_url_2 = zope.schema.URI(
        title=_('URL for topiclink #2'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    topiclink_url_3 = zope.schema.URI(
        title=_('URL for topiclink #3'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    topiclink_url_4 = zope.schema.URI(
        title=_('URL for topiclink #4'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    topiclink_url_5 = zope.schema.URI(
        title=_('URL for topiclink #5'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )


class ILiveblogLinks(zope.interface.Interface):
    liveblog_label_1 = zope.schema.TextLine(title=_('Label for liveblog #1'), required=False)

    liveblog_label_2 = zope.schema.TextLine(title=_('Label for liveblog #2'), required=False)

    liveblog_label_3 = zope.schema.TextLine(title=_('Label for liveblog #3'), required=False)

    liveblog_url_1 = zope.schema.URI(
        title=_('URL for liveblog #1'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    liveblog_url_2 = zope.schema.URI(
        title=_('URL for liveblog #2'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )

    liveblog_url_3 = zope.schema.URI(
        title=_('URL for liveblog #3'),
        required=False,
        constraint=zeit.cms.interfaces.valid_link_target,
    )


class ICenterPage(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent,
    zeit.edit.interfaces.IContainer,
    ITopicLinks,
    ILiveblogLinks,
    zeit.retresco.interfaces.ISkipEnrich,
):
    type = zope.schema.Choice(
        title=_('CP type'), source=zeit.content.cp.source.CPTypeSource(), default='centerpage'
    )

    body = zope.interface.Attribute('Convenience access to IEditableBody')

    topiclink_title = zope.schema.TextLine(title=_('Name for topiclinks'), required=False)

    og_title = zope.schema.TextLine(title=_('Titel'), required=False)

    og_description = zope.schema.TextLine(title=_('Description'), required=False)

    og_image = zope.schema.TextLine(title=_('Image'), required=False)

    keywords = zeit.cms.tagging.interfaces.Keywords(required=False, default=())

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

    cache = zope.interface.Attribute(
        """\
        Returns a (transaction bound) cache, which can be used for various
        things like rendered areas, teaser contents, query objects etc."""
    )

    cached_areas = zope.interface.Attribute(
        """\
        Cached list of all IArea objects; IContentQuery uses this instead of
        iterating over body/regions/values, for performance reasons."""
    )


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

    visible = zope.schema.Bool(title=_('Visible in frontend'), default=True)


class IBody(zeit.edit.interfaces.IArea, IElement):
    """Container of the CenterPage that actually contains the children."""


class IReadRegion(zeit.edit.interfaces.IReadContainer):
    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)

    title = zope.schema.TextLine(title=_('Title'), required=False)

    __name__ = zope.schema.TextLine(title=_('Name'), required=True)

    # XXX We need to repeat these from IElement for security declarations.
    visible = zope.schema.Bool(title=_('Visible in frontend'), default=True)

    kind = zope.schema.TextLine(title=_('Kind'))

    kind_title = zope.schema.TextLine(title=_('Kind Title'))


class IWriteRegion(zeit.edit.interfaces.IWriteContainer):
    pass


class IRegion(IReadRegion, IWriteRegion, zeit.edit.interfaces.IContainer, IElement):
    """Abstract layer above IArea."""

    zope.interface.invariant(zeit.edit.interfaces.unique_name_invariant)


class AutomaticTypeSource(zeit.cms.content.sources.SimpleDictSource):
    values = {
        'centerpage': _('automatic-area-type-centerpage'),
        'custom': _('automatic-area-type-custom'),
        'topicpage': _('automatic-area-type-topicpage'),
        'related-topics': _('automatic-area-type-related-topics'),
        'elasticsearch-query': _('automatic-area-type-elasticsearch-query'),
        'reach': _('automatic-area-type-reach'),
        'topicpagelist': _('automatic-area-type-topicpagelist'),
        'rss-feed': _('automatic-area-type-rss-feed'),
        'sql-query': _('automatic-area-type-sql-query'),
    }

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

    if data.automatic_type == 'elasticsearch-query' and data.elasticsearch_raw_query:
        return True

    if data.automatic_type == 'rss-feed' and data.rss_feed:
        return True

    if data.automatic_type == 'reach' and data.reach_service:
        return True

    if data.automatic_type == 'topicpagelist':
        return True

    if data.automatic_type == 'sql-query' and data.sql_query:
        return True

    return False


class IReadArea(zeit.edit.interfaces.IReadContainer, ITopicLinks, IConfiguration):
    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)

    # XXX We need to repeat this from IElement for security declarations.
    visible = zope.schema.Bool(title=_('Visible in frontend'), default=True)

    kind = zope.schema.TextLine(
        title=_('Kind'), description=_('Used internally for rendering on Friedbert'), default='solo'
    )

    kind_title = zope.interface.Attribute('Translation of kind to a human friendly information')

    supertitle = zope.schema.TextLine(title=_('Supertitle'), required=False)

    title = zope.schema.TextLine(title=_('Title'), required=False)

    read_more = zope.schema.TextLine(title=_('Read more'), required=False)

    read_more_url = zope.schema.URI(
        title=_('Read more URL'), required=False, constraint=zeit.cms.interfaces.valid_link_target
    )

    image = zope.schema.Choice(
        title=_('Image'),
        description=_('Drag an image group here'),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource,
    )

    apply_teaser_layouts_automatically = zope.schema.Bool(
        title=_('Apply teaser layouts automatically?'), required=False, default=False
    )

    first_teaser_layout = zope.schema.Choice(
        title=_('First teaser layout'),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource(),
        required=False,
    )

    default_teaser_layout = zope.interface.Attribute(
        'Default layout for teaser lists inside this area'
    )

    automatic = zope.schema.Bool(title=_('automatic'), default=False)
    automatic.__doc__ = """If True, IRenderedArea.values() will populate
    any IAutomaticTeaserBlock with content, as specified by automatic_type.
    """
    # XXX really ugly styling hack
    automatic.setTaggedValue('placeholder', ' ')

    automatic_type = zope.schema.Choice(
        title=_('Automatic type'), source=AutomaticTypeSource(), required=True
    )

    background_color = zope.schema.TextLine(
        title=_('Area background color (6 characters, no #)'),
        description=_('Hex value of background color for area'),
        required=False,
        min_length=6,
        max_length=6,
        constraint=zeit.cms.content.interfaces.hex_literal,
    )

    @zope.interface.invariant
    def automatic_type_required_arguments(data):
        if data.automatic and not automatic_area_can_read_teasers_automatically(data):
            if data.automatic_type == 'centerpage':
                error_message = _(
                    'Automatic area with teaser from centerpage '
                    'requires a referenced centerpage.'
                )
            if data.automatic_type == 'custom':
                error_message = _(
                    'Automatic area with teaser from custom query ' 'requires a query condition.'
                )
            if data.automatic_type == 'topicpage':
                error_message = _(
                    'Automatic area with teaser from TMS topicpage ' 'requires a topicpage ID.'
                )
            if data.automatic_type == 'elasticsearch-query':
                error_message = _(
                    'Automatic area with teaser from elasticsearch query ' 'requires a raw query.'
                )
            if data.automatic_type == 'rss-feed':
                error_message = _('Automatic area with rss-feed requires a given feed')
            if data.automatic_type == 'related-topics':
                error_message = _(
                    'Automatic area with related-topics requires a given' ' topicpage'
                )
            if data.automatic_type == 'reach':
                error_message = _('Automatic area with teasers from reach require a given' ' kind')
            raise zeit.cms.interfaces.ValidationError(error_message)
        return True

    @zope.interface.invariant
    def elasticsearch_valid_json_query(data):
        """Check the es raw query is plausible elasticsearch DSL"""
        if data.automatic_type == 'elasticsearch-query' and (data.elasticsearch_raw_query):
            try:
                query = json.loads(data.elasticsearch_raw_query)
                if 'query' not in query:
                    raise ValueError('Top-level key "query" is required.')
            except Exception as err:
                raise zeit.cms.interfaces.ValidationError(
                    _('Elasticsearch raw query is malformed: %s' % err)
                )
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
    """Overrides values() to evaluate any automatic settings."""

    start = zope.interface.Attribute(
        'Offset the IContentQuery result by this many content objects. '
        'This is an extension point for zeit.web to do pagination.'
    )


class ITeaseredContent(zope.interface.common.sequence.IReadSequence):
    """Returns an iterable content objects in a CenterPage, that are referenced
    by ITeaserBlocks, in the same order they appear in the CenterPage.
    """


class IBlock(IElement, zeit.edit.interfaces.IBlock):
    supertitle = zope.schema.TextLine(title=_('Supertitle'), required=False)
    title = zope.schema.TextLine(title=_('Title'), required=False)
    type_title = zope.interface.Attribute('Translation of type to a human friendly information')
    volatile = zope.schema.Bool(
        title=_('Whether block can be removed by automation, e.g. AutoPilot'), default=False
    )

    # BBB needed by zeit.web for legacy/zmo content only
    read_more = zope.schema.TextLine(title=_('Read more'), required=False)
    read_more_url = zope.schema.URI(
        title=_('Read more URL'), required=False, constraint=zeit.cms.interfaces.valid_link_target
    )


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


class IEntry(zope.interface.Interface):
    """An entry in a feed."""

    pinned = zope.schema.Bool(title=_('Pinned'))

    hidden = zope.schema.Bool(title=_('Hidden on HP'))

    big_layout = zope.schema.Bool(title=_('Big layout'))

    hidden_relateds = zope.schema.Bool(title=_('Hidden relateds'))


class IReadFeed(zope.interface.Interface):
    """Feed read interface."""

    title = zope.schema.TextLine(title=_('Title'))
    object_limit = zope.schema.Int(
        title=_('Limit amount'),
        description=_('limit-amount-description'),
        default=50,
        min=1,
        required=False,
    )

    def __len__():
        """Return amount of objects syndicated."""

    def __iter__():
        """Iterate over published content.

        When content is pinned __iter__ is supposed to return pinned content
        at the right position.

        """

    def __contains__(content):
        """Return if content is syndicated in this channel."""

    def getPosition(content):
        """Returns the position of `content` in the feed.

        Returns 1-based position of the content object in the feed or None if
        the content is not syndicated in this feed.

        """

    def getMetadata(content):
        """Returns IEntry instance corresponding to content."""


class IWriteFeed(zope.interface.Interface):
    """Feed write interface."""

    def insert(position, content):
        """Add `content` to self at position `position`."""

    def append(content):
        """Add `content` to self at end."""

    def remove(content):
        """Remove `content` from feed.

        raises ValueError if `content` not in feed.

        """

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is a list or a tuple containing the set of existing keys in
        the new order. `order` must contain ``len(keys())`` items and cannot
        contain duplicate keys.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """

    def updateMetadata(content):
        """Update the metadata of a contained object.

        Raises KeyError if the content is not syndicated in this feed.

        """


class IFeed(IReadFeed, IWriteFeed):
    """Documents can be published into a feed."""


class IReadTeaserBlock(IBlock, IReadFeed):
    references = zope.schema.Choice(
        title=_('Referenced content'),
        description=_('Drag content here'),
        source=zeit.cms.content.contentsource.cmsContentSource,
        required=False,
    )

    layout = zope.schema.Choice(
        title=_('Layout'), source=zeit.content.cp.layout.TeaserBlockLayoutSource()
    )

    force_mobile_image = zope.schema.Bool(title=_('Force image on mobile'), default=True)


class IWriteTeaserBlock(IWriteFeed):
    def update(other):
        """Copy content and properties from another ITeaserBlock."""


class ITeaserBlock(IReadTeaserBlock, IWriteTeaserBlock):
    """This module references a content object."""


class IReadLocalTeaserBlock(IReadTeaserBlock):
    teaserSupertitle = zope.schema.TextLine(title=_('Teaser kicker'), required=False)

    teaserTitle = zope.schema.TextLine(title=_('Teaser title'), required=False)

    teaserText = zope.schema.Text(title=_('Teaser text'), required=False)

    # Implementing a separate IImages adapter for ILocalTeaserBlock seems way
    # more effort than it's worth, so we include the two fields here instead.
    # But we don't inherit from IImages, since zeit.web would not be able to
    # override that, and it needs to apply IImages to the teasered content
    # object, instead of the module.
    image = zeit.content.image.interfaces.IImages['image']
    fill_color = zeit.content.image.interfaces.IImages['fill_color']


class IWriteLocalTeaserBlock(IWriteTeaserBlock):
    pass


class ILocalTeaserBlock(IReadLocalTeaserBlock, IWriteLocalTeaserBlock, ITeaserBlock):
    """Teaser module that allows overriding title/text/image"""


class IWriteAutomaticTeaserBlock(IWriteTeaserBlock):
    def change_layout(layout):
        """Temporarily change the layout (for the duration of one area.values()
        evaluation)."""

    def materialize():
        """Convert this block to a normal ITeaserBlock, filled with the
        current automatic content.
        """


class IAutomaticTeaserBlock(IReadTeaserBlock, IWriteAutomaticTeaserBlock, ITeaserBlock):
    pass


def validate_xml_block(xml):
    if xml.tag != 'container':
        raise zeit.cms.interfaces.ValidationError(_('The root element must be <container>.'))
    if xml.get('{http://namespaces.zeit.de/CMS/cp}type') != 'xml':
        raise zeit.cms.interfaces.ValidationError(_("cp:type must be 'xml'."))
    if not xml.get('{http://namespaces.zeit.de/CMS/cp}__name__'):
        raise zeit.cms.interfaces.ValidationError(_('No or empty cp:__name__ attribute.'))
    return True


class IXMLBlock(IBlock):
    """A block containing raw XML."""

    xml = zeit.cms.content.field.XMLTree(
        title=_('XML Source'), constraint=validate_xml_block, tidy_input=True
    )


class ICPExtraBlock(IBlock):
    """Block which contains a cp_extra."""

    cpextra = zope.schema.Choice(
        title=_('CP Extra Id'), source=zeit.content.cp.source.CPExtraSource()
    )


class IQuizBlock(zeit.content.modules.interfaces.IQuiz, IBlock):
    pass


class IRenderedXML(zope.interface.Interface):
    """Recursively converts a CenterPage to an lxml tree."""


class IRawTextBlock(zeit.content.modules.interfaces.IRawText, IBlock):
    pass


class IHeaderImageBlock(IBlock):
    image = zope.schema.Choice(
        title=_('Image'),
        description=_('Drag an image group here'),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource,
    )
    animate = zope.schema.Bool(title=_('Animate'), default=False)


class AlignmentSource(zeit.cms.content.sources.SimpleDictSource):
    values = {
        'left': _('left'),
        'center': _('center'),
        'right': _('right'),
    }


class IMarkupBlock(IBlock):
    text = zope.schema.Text(title=_('Contents'), description=_('Use Markdown'), required=True)
    markdown = zope.interface.Attribute('Text in markdown format')
    alignment = zope.schema.Choice(
        title=_('Alignment'),
        description=_('Choose alignment'),
        source=AlignmentSource(),
        default='left',
    )


class CardstackColorSource(zeit.cms.content.sources.SimpleDictSource):
    values = {
        color: color
        for color in [
            '#D8D8D8',
            '#5E534F',
            '#E4DED8',
            '#69696C',
            '#FF7783',
            '#7C0E14',
            '#6FA6B9',
            '#085064',
            '#57C494',
            '#1E6847',
        ]
    }


class ICardstackBlock(IBlock):
    card_id = zope.schema.TextLine(title=_('Cardstack id'))

    is_advertorial = zope.schema.Bool(title=_('Advertorial?'), default=False)

    cardstack_background_color = zope.schema.Choice(
        title=_('Background color'),
        description=_('Choose a background color'),
        source=CardstackColorSource(),
    )


JOBTICKER_SOURCE = zeit.content.modules.jobticker.FeedSource(ICenterPage)


class IJobTickerBlock(zeit.content.modules.interfaces.IJobTicker, IBlock):
    """The Jobticker block with a specific feed specified in source."""

    feed = zope.schema.Choice(title=_('Jobbox Ticker'), required=True, source=JOBTICKER_SOURCE)


class IMailBlock(zeit.content.modules.interfaces.IMail, IBlock):
    pass


class INewsletterSignupBlock(zeit.content.modules.interfaces.INewsletterSignup, IBlock):
    pass


# BBB We don't need this anymore, but existing content still has it.
class ICP2015(ICenterPage):
    """Marker interfaces for CPs edited by the current CP-Editor (master)."""


class ICpSEO(zeit.seo.interfaces.ISEO):
    enable_rss_tracking_parameter = zope.schema.Bool(
        title=_('Enable RSS Tracking-Parameter'), required=False
    )
