# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
from zeit.content.cp.layout import ITeaserBlockLayout, ITeaserBarLayout
import urlparse
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.cp.blocks.avsource
import zeit.content.cp.layout
import zeit.content.cp.source
import zeit.content.image.interfaces
import zeit.content.quiz.source
import zeit.edit.interfaces
import zeit.workflow.interfaces
import zope.container.interfaces
import zope.interface


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.content.cp'


class ValidationError(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zope.container.interfaces.IReadContainer):
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


class IValidatingWorkflow(zeit.workflow.interfaces.ITimeBasedPublishing):
    pass


class IReadRegion(zeit.edit.interfaces.IReadContainer):
    pass


class IWriteRegion(zeit.edit.interfaces.IWriteContainer):
    pass


# IRegion wants to be an IArea, but also preserve the IReadArea/IWriteArea
# split, so we inherit from IArea again. Absolutely no thanks to Zope for this
# whole read/write business :-(
class IRegion(IReadRegion, IWriteRegion, zeit.edit.interfaces.IContainer):
    """A region contains blocks."""


class ILead(IRegion):
    """The lead region."""


class IInformatives(IRegion):
    """The informatives region."""


class IMosaic(zeit.edit.interfaces.IContainer):
    """Teaser mosaic."""


class ICMSContentIterable(zope.interface.Interface):
    """An iterable object iterating over CMSContent."""

    def __iter__():
        pass


class ICPFeed(zope.interface.Interface):
    """Feed section of a CenterPage"""

    items = zope.interface.Attribute("tuple of feed items")


class IBlock(zeit.edit.interfaces.IBlock):

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False)

    publisher  = zope.schema.TextLine(
        title=_("Publisher"),
        required=False)
    publisher_url = zope.schema.TextLine(
        title=_("Publisher URL"),
        required=False)

    supertitle  = zope.schema.TextLine(
        title=_("Supertitle"),
        required=False)
    supertitle_url = zope.schema.TextLine(
        title=_("Supertitle URL"),
        required=False)

    read_more = zope.schema.TextLine(
        title=_("Read more"),
        required=False)
    read_more_url = zope.schema.TextLine(
        title=_("Read more URL"),
        required=False)


class IPlaceHolder(IBlock):
    """Placeholder."""


#
# Teaser block (aka teaser list)
#


class IReadTeaserBlock(IBlock, zeit.cms.syndication.interfaces.IReadFeed):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBlockLayoutSource())


class AutopilotSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'autopilot'
    check_interfaces = (
        ICenterPage,
        zeit.cms.syndication.interfaces.IFeed,
    )

autopilotSource = AutopilotSource()


class IAutoPilotReadTeaserBlock(IReadTeaserBlock):

    referenced_cp = zope.schema.Choice(
        title=_('Get teasers from (autopilot)'),
        source=autopilotSource,
        required=False)

    autopilot = zope.schema.Bool(
        title=_('Autopilot active'))

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    @zope.interface.invariant
    def autopilot_requires_referenced_cp(self):
        if self.autopilot and not self.referenced_cp:
            raise zope.schema.ValidationError(
                _("Cannot activate autopilot without referenced centerpage"))
        return True


class IWriteTeaserBlock(zeit.cms.syndication.interfaces.IWriteFeed):
    pass


class ITeaserBlock(IReadTeaserBlock, IWriteTeaserBlock):
    """A list of teasers."""


class IAutoPilotTeaserBlock(IAutoPilotReadTeaserBlock, ITeaserBlock):
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


def validate_xml_block(xml):
    if xml.tag != 'container':
        raise ValidationError(_("The root element must be <container>."))
    if xml.get('{http://namespaces.zeit.de/CMS/cp}type') != 'xml':
        raise ValidationError(_("cp:type must be 'xml'."))
    if not xml.get('{http://namespaces.zeit.de/CMS/cp}__name__'):
        raise ValidationError(_("No or empty cp:__name__ attribute."))
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


class InvalidFeedURL(zope.schema.interfaces.ValidationError):

    def doc(self):
        return self.args[0]


def valid_feed_url(uri):
    zope.schema.URI().fromUnicode(uri)  # May raise InvalidURI
    if urlparse.urlparse(uri).scheme in ('http', 'https', 'file'):
        return True
    # NOTE: we hide the fact that we support (some) file urls.
    raise InvalidFeedURL(_('Only http and https are supported.'))


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
        title=_("If parsing the feed fails, the error message is stored here."))

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



class IReadTeaserBar(IReadRegion, zeit.edit.interfaces.IElement):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBarLayoutSource(),
        default=zeit.content.cp.layout.get_bar_layout('normal'))


class IWriteTeaserBar(IWriteRegion):
    pass


class ITeaserBar(IReadTeaserBar, IWriteTeaserBar, IRegion):
    """A teaser bar is a bar in the teaser mosaic.

    The TeaserBar has a dual nature of being both a block and a region.

    """


class IRuleGlobs(zope.interface.Interface):
    """Adapt to this to convert the context to a dictionary of things of
    interest to an IRule XXX docme"""


class IRuleGlob(zope.interface.Interface):
    """XXX docme"""


class IRulesManager(zope.interface.Interface):
    """Collects all validation rules."""

    rules = zope.schema.List(title=u"A list of rules.")


class IValidator(zope.interface.Interface):
    """Validate a centerpage element."""

    status = zope.schema.TextLine(
        title=u"Validation status: {None, warning, error}")

    messages = zope.schema.List(
        title=u"List of error messages.")


class IQuizBlock(IBlock):
    """The Quiz block with a reference to a quiz."""

    referenced_quiz = zope.schema.Choice(
        title=_("Quiz"),
        source=zeit.content.quiz.source.QuizSource())


class IFullGraphicalBlock(IBlock):
    """The Fullgraphical block with a reference to an object and an image."""

    referenced_object = zope.schema.Choice(
        title=_("Link to"),
        source=zeit.cms.content.contentsource.CMSContentSource())

    image = zope.schema.Choice(
        title=_("Image"),
        source=zeit.content.image.interfaces.ImageSource())
