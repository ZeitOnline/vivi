# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
from zeit.content.cp.layout import ITeaserBlockLayout, ITeaserBarLayout
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.cp.blocks.avsource
import zeit.content.cp.layout
import zeit.content.image.interfaces
import zeit.content.quiz.source
import zeit.workflow.interfaces
import zope.container.interfaces
import zope.interface


class ValidationError(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


class CPTypeSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-types-url'

    def getValues(self):
        tree = self._get_tree()
        return [unicode(item.get('name'))
                for item in tree.iterchildren()]

    def getTitle(self, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        return unicode(tree.xpath('/centerpage-types/type[@name = "%s"]' %
                                  value)[0])


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zope.container.interfaces.IReadContainer):
    """A relaunch 09 centerpage."""

    type = zope.schema.Choice(
        title=_('CP type'),
        required=False,
        source=CPTypeSource(),
        missing_value=u'centerpage')

    header_image = zope.schema.Choice(
        title=_('Header image'),
        required=False,
        source=zeit.content.image.interfaces.ImageSource())

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

    def verify_interface(self, value):
        return ICenterPage.providedBy(value)


centerPageSource = CenterPageSource()


class IValidatingWorkflow(zeit.workflow.interfaces.ITimeBasedPublishing):
    pass


class IReadContainer(zeit.cms.content.interfaces.IXMLRepresentation,
                zope.container.interfaces.IContained,
                zope.container.interfaces.IReadContainer):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """

class IWriteContainer(zope.container.interfaces.IOrdered):
    """Modify area."""

    def add(item):
        """Add item to container."""

    def __delitem__(key):
        """Remove item."""


class IContainer(IReadContainer, IWriteContainer):
    pass


class IArea(IContainer):
    """Combined read/write interface to areas."""


class IReadRegion(IReadContainer):
    pass


class IWriteRegion(IWriteContainer):
    pass


# IRegion wants to be an IArea, but also preserve the IReadArea/IWriteArea
# split, so we inherit from IArea again. Absolutely no thanks to Zope for this
# whole read/write business :-(
class IRegion(IReadRegion, IWriteRegion, IContainer):
    """A region contains blocks."""


class ILead(IRegion):
    """The lead region."""


class IInformatives(IRegion):
    """The informatives region."""


class IMosaic(IContainer):
    pass

class IElement(zope.interface.Interface):
    """XXX A module which can be instantiated and added to the page."""

    type = zope.interface.Attribute("Type identifier.")


class ICMSContentIterable(zope.interface.Interface):
    """An iterable object iterating over CMSContent."""

    def __iter__():
        pass


class IElementFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Block type'))

    def __call__():
        """Create block."""


class IBlock(IElement):

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
        source=zeit.content.cp.layout.TeaserBlockLayoutSource(),
        missing_value=zeit.content.cp.layout.get_layout('leader'))


class IAutoPilotReadTeaserBlock(IReadTeaserBlock):

    referenced_cp = zope.schema.Choice(
        title=_("Get teasers from (autopilot)"),
        source=zeit.cms.content.contentsource.CMSContentSource(),
        required=False)
    autopilot = zope.schema.Bool(
        title=_("Autopilot active")
        )

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
        constraint=validate_xml_block)


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


class IFeed(zeit.cms.content.interfaces.IXMLContent,
            zeit.cms.interfaces.IAsset):

    url = zope.schema.TextLine(
        title=_("RSS feed URL (http://...)"))

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

    url = zope.schema.TextLine(
        title=_("URL to RSS feed (http://...)."))

    feed = zope.interface.Attribute("The corresponding IFeed object.")


class ICPExtraBlock(IBlock):
    """Block which contains a cp_extra."""

    title = zope.schema.TextLine(
        title=u'Title of the cp_extra.')


class ITeaser(zeit.cms.content.interfaces.ICommonMetadata,
              zeit.cms.content.interfaces.IXMLContent):
    """A standalone teaser object which references the article."""

    original_content = zope.schema.Choice(
        title=u'The referenced article.',
        source=zeit.cms.content.contentsource.cmsContentSource)


class IReadTeaserBar(IReadRegion, IElement):

    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.TeaserBarLayoutSource(),
        missing_value=zeit.content.cp.layout.get_layout('normal'))


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
