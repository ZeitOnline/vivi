from zeit.cms.i18n import MessageFactory as _
import zc.form.field
import zc.form.interfaces
import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.wochenmarkt.sources
import zope.container.interfaces
import zope.interface
import zope.interface.common.sequence
import zope.interface.interfaces
import zope.schema
import zope.schema.interfaces


# XXX There is too much, too unordered in here, clean this up.


# prevent circular import
from zeit.cms.content.contentsource import ICMSContentSource  # noqa
from zeit.cms.content.contentsource import INamedCMSContentSource  # noqa
from zeit.cms.content.contentsource import IAutocompleteSource  # noqa


class IAuthorType(zeit.cms.interfaces.ICMSContentType):
    """Interface type for authors."""


@zope.interface.implementer(zeit.cms.content.contentsource.IAutocompleteSource)
class AuthorSource(zeit.cms.content.contentsource.CMSContentSource):

    check_interfaces = IAuthorType
    name = 'authors'


authorSource = AuthorSource()


class AgencySource(AuthorSource):

    name = 'agencies'
    additional_query_conditions = {'author_type': 'Agentur'}


agencySource = AgencySource()


class IChannelField(zc.form.interfaces.ICombinationField):
    """Marker interface so we can register a specialized widget
    for this field."""


class ReferenceField(zope.schema.Choice):

    def _validate(self, value):
        if self._init_field:
            return
        # skip immediate superclass, since that's what we want to change
        super()._validate(value)
        if value.target not in self.vocabulary:
            raise zope.schema.interfaces.ConstraintNotSatisfied(value)


class ICommonMetadata(zope.interface.Interface):

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=54,
        required=False)

    page = zope.schema.Int(
        title=_("Page"),
        readonly=True,
        required=False)

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.RessortSource())

    sub_ressort = zope.schema.Choice(
        title=_('Sub ressort'),
        source=zeit.cms.content.sources.SubRessortSource(),
        required=False)

    channels = zope.schema.Tuple(
        title=_('Channels'),
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
    zope.interface.alsoProvides(channels.value_type, IChannelField)

    lead_candidate = zope.schema.Bool(
        title=_('Lead candidate'),
        default=True,
        required=False)

    printRessort = zope.schema.TextLine(
        title=_("Print ressort"),
        readonly=True,
        required=False,
        default='n/a')

    # not required since e.g. Agenturmeldungen don't have an author, only
    # a copyright notice
    authorships = zope.schema.Tuple(
        title=_("Authors"),
        value_type=ReferenceField(source=authorSource),
        default=(),
        required=False)
    authorships.value_type.setTaggedValue(
        'zeit.cms.addform.contextfree', 'zeit.content.author.add_contextfree')

    # DEPRECATED, use authorships instead
    # (still used by zeit.vgwort for querying)
    authors = zope.schema.Tuple(
        title=_("Authors (freetext)"),
        value_type=zope.schema.TextLine(),
        required=False,
        default=('',),
        description=_('overwritten if any non-freetext authors are set'))

    agencies = zope.schema.Tuple(
        title=_("Agencies"),
        value_type=zope.schema.Choice(source=agencySource),
        default=(),
        required=False)

    access = zope.schema.Choice(
        title=_('Access'),
        default='free',
        source=zeit.cms.content.sources.ACCESS_SOURCE)

    keywords = zeit.cms.tagging.interfaces.Keywords(
        required=False,
        default=())

    recipe_categories = zope.schema.Tuple(
        title=_("Recipe Categories"),
        value_type=zope.schema.Choice(
            source=zeit.wochenmarkt.sources.RecipeCategoriesSource()),
        default=(),
        required=False)

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

    copyrights = zope.schema.TextLine(
        title=_("Copyright (c)"),
        description=_("Do not enter (c)."),
        required=False)

    supertitle = zope.schema.TextLine(
        title=_("Kicker"),
        description=_("Please take care of capitalisation."),
        required=False,
        max_length=70)

    # DEPRECATED, use authorships instead (still used by
    # k4import/exporter.zeit.de to transmit author information *into* vivi,
    # so Producing can manually convert it to authorships)
    byline = zope.schema.TextLine(
        title=_("By line"),
        readonly=True,
        required=False)

    title = zope.schema.Text(
        title=_("Title"),
        missing_value='')

    title.setTaggedValue('zeit.cms.charlimit', 70)

    subtitle = zope.schema.Text(
        title=_("Subtitle"),
        missing_value='',
        required=False)

    subtitle.setTaggedValue('zeit.cms.charlimit', 170)

    teaserTitle = zope.schema.TextLine(
        title=_("Teaser title"),
        required=False,
        max_length=70)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    teaserSupertitle = zope.schema.TextLine(
        title=_('Teaser kicker'),
        description=_('Please take care of capitalisation.'),
        required=False,
        max_length=70)

    vg_wort_id = zope.schema.TextLine(
        title=_('VG Wort Id'),
        required=False)

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily newsletter"),
        description=_(
            "Should this article be listed in the daily newsletter?"),
        required=False,
        default=True)

    commentsPremoderate = zope.schema.Bool(
        title=_("Comments premoderate"),
        required=False,
        default=False)

    commentsAllowed = zope.schema.Bool(
        title=_("Comments allowed"),
        required=False,
        default=True)

    commentSectionEnable = zope.schema.Bool(
        title=_("Show commentthread"),
        required=False,
        default=True)

    banner = zope.schema.Bool(
        title=_("Banner"),
        required=False,
        default=True)

    banner_content = zope.schema.Bool(
        title=_("Banner in Content"),
        required=False,
        default=True)

    banner_outer = zope.schema.Bool(
        title=_("Banner Mainad"),
        required=False,
        default=True)

    banner_id = zope.schema.TextLine(
        title=_('Banner id'),
        required=False)

    hide_adblocker_notification = zope.schema.Bool(
        title=_('Hide AdBlocker notification'),
        default=False,
        required=False)

    product = zope.schema.Choice(
        title=_('Product id'),
        # XXX kludgy, we expect a product with this ID to be present in the XML
        # file. We only need to set an ID here, since to read the product we'll
        # ask the source anyway.
        default=zeit.cms.content.sources.Product('ZEDE'),
        source=zeit.cms.content.sources.PRODUCT_SOURCE)

    overscrolling = zope.schema.Bool(
        title=_('Overscrolling'),
        required=False,
        default=True)

    cap_title = zope.schema.TextLine(
        title=_('CAP title'),
        required=False)

    deeplink_url = zope.schema.URI(
        title=_('Deeplink URL'),
        required=False,
        default=None)

    tldr_title = zope.schema.TextLine(
        title=_("tldr title"),
        required=False,
        max_length=70)

    tldr_text = zope.schema.Text(
        title=_("tldr text"),
        required=False,
        max_length=450)

    tldr_milestone = zope.schema.Bool(
        title=_("tldr milestone"),
        required=False,
        default=False)

    tldr_date = zope.schema.Datetime(
        title=_("tldr date"),
        required=False)

    storystreams = zope.schema.Tuple(
        title=_("Storystreams"),
        value_type=zope.schema.Choice(
            source=zeit.cms.content.sources.StorystreamSource()),
        default=(),
        required=False)

    advertisement_title = zope.schema.TextLine(
        title=_("Advertisement title"),
        required=False)

    advertisement_text = zope.schema.Text(
        title=_("Advertisement text"),
        required=False)

    ir_mediasync_id = zope.schema.TextLine(
        title=_("InterRed MediaSync ID"),
        required=False,
        readonly=True)

    ir_article_id = zope.schema.TextLine(
        title=_("InterRed Article ID"),
        required=False,
        readonly=True)


class IProduct(zope.interface.Interface):
    """A publication product"""

    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    vgwortcode = zope.interface.Attribute('VGWort code, optional')
    href = zope.interface.Attribute('URL for the "homepage" of this product')
    target = zope.interface.Attribute('Optional link target (e.g. _blank)')
    show = zope.interface.Attribute(
        'Flag what to display in frontend byline. {issue,link,source}')
    volume = zope.interface.Attribute('Boolean: has print volumes')
    location = zope.interface.Attribute(
        'uniqueId template of the IVolumes of this product, '
        'e.g. http://xml.zeit.de/{year}/{name}/ausgabe')
    centerpage = zope.interface.Attribute(
        'uniqueId template for the public-facing CP of this product, '
        'e.g. http://xml.zeit.de/{year}/{name}/index')
    cp_template = zope.interface.Attribute(
        'uniqueId of a zeit.content.text.interfaces.IPythonScript, which is '
        'used to create the public-facing CP of this product')
    autochannel = zope.interface.Attribute(
        'Set false to suppress setting channel on ressort changes')
    relates_to = zope.interface.Attribute(
        'Product-ID of another Product we belong to')
    dependent_products = zope.interface.Attribute(
        'List of products whose relates_to points to us')


class ISerie(zope.interface.Interface):

    id = zope.interface.Attribute('')
    title = zope.interface.Attribute('')
    serienname = zope.interface.Attribute('')
    url = zope.interface.Attribute('')
    encoded = zope.interface.Attribute('')
    column = zope.interface.Attribute('')
    video = zope.interface.Attribute('')


class IStorystreamReference(zope.interface.Interface):

    id = zope.interface.Attribute('')
    title = zope.interface.Attribute('')
    references = zope.interface.Attribute('')


def hex_literal(value):
    try:
        int(value, base=16)
    except ValueError:
        raise zeit.cms.interfaces.ValidationError(_("Invalid hex literal"))
    else:
        return True


WRITEABLE_ON_CHECKIN = object()
WRITEABLE_LIVE = object()
WRITEABLE_ALWAYS = object()


class IDAVPropertyConverter(zope.interface.Interface):
    """Parse a unicode string from a DAV property to a value and vice versa."""

    def fromProperty(value):
        """Convert property value to python value.

        returns python object represented by value.

        raises ValueError if the value could not be converted.
        raises zope.schema.ValidationError if the value could be converted but
        does not satisfy the constraints.

        """

    def toProperty(value):
        """Convert python value to DAV property value.

        returns unicode
        """


class IGenericDAVPropertyConverter(IDAVPropertyConverter):
    """A dav property converter which converts in a generic way.

    This interface is a marker if some code wants to know if a generic
    converter or a specialised is doing the work.

    """


class IDAVToken(zope.interface.Interface):
    """A string representing a token that uniquely identifies a value."""


class IDAVPropertyChangedEvent(zope.interface.interfaces.IObjectEvent):
    """A dav property has been changed."""

    old_value = zope.interface.Attribute("The value before the change.")
    new_value = zope.interface.Attribute("The value after the change.")

    property_namespace = zope.interface.Attribute("Webdav property namespace.")
    property_name = zope.interface.Attribute("Webdav property name.")

    field = zope.interface.Attribute(
        "zope.schema field the property was changed for.")


@zope.interface.implementer(IDAVPropertyChangedEvent)
class DAVPropertyChangedEvent(zope.interface.interfaces.ObjectEvent):

    def __init__(self, object, property_namespace, property_name,
                 old_value, new_value, field):
        self.object = object
        self.property_namespace = property_namespace
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.field = field


class ITextContent(zope.interface.Interface):
    """Representing text content XXX"""

    data = zope.schema.Text(title=u"Document content")


class IXMLRepresentation(zope.interface.Interface):
    """Objects with an XML representation."""

    xml = zeit.cms.content.field.XMLTree(
        title=_("XML Source"))


class IXMLReference(zope.interface.Interface):
    """XML representation of an object reference.

    How the object references is serialized is dependent on both the target
    object and the type of reference. For instance, a feed might usually
    use an <xi:include> tag, while an image uses <img>. And then there
    might be references inside the <head> that always use a <reference> tag.
    (NOTE: These are just examples, not actual zeit.cms policy!)

    Adapting to IXMLReference yields an lxml.objectify tree::

        node = zope.component.getAdapter(
           content, zeit.cms.content.interfaces.IXMLReference, name='image')

    The target uniqueId is always stored in the ``href`` attribute of the node.
    """


class IXMLReferenceUpdater(zope.interface.Interface):
    """Objects that update metadata etc on XML references."""

    def update(xml_node, suppress_errors=False):
        """Update xml_node with data from the content object.

        xml_node: lxml.objectify'ed element
        """


class IReference(IXMLRepresentation,
                 zeit.cms.interfaces.ICMSContent,
                 zope.location.interfaces.ILocation):
    """Reference to an ICMSContent object (optionally with properties of its
    own).

    To deserialize an IXMLReference, adapt the source ICMSContent and the XML
    node to IReference (using the same adapter name that was used to create the
    IXMLReference)::

        reference = zope.component.getMultiAdapter(
            (source, node), zeit.cms.content.interfaces.IReference,
            name='image')


    For widget support (DropObjectWidget/ObjectSequenceWidget), IReference
    can be resolved as ICMSContent, using a uniqueId built from
    "source uniqueId, source attribute name, target uniqueId".
    """

    target = zope.interface.Attribute('The referenced ICMSContent object')
    target_unique_id = zope.interface.Attribute(
        'uniqueId of the referenced ICMSContent object')
    attribute = zope.interface.Attribute(
        'Attribute name of reference property on source')

    def create(target, suppress_errors=False):
        """Create a new references from our source to the given target
        (either an ICMSContent or a uniqueId)."""

    def get(target, default=None):
        """If our source has a reference to the given target
        (ICMSContent or uniqueId), return that, else return default."""

    def update_metadata(suppress_errors=False):
        """Run XMLReferenceUpdater on our XML node."""


class IReferences(zope.interface.common.sequence.IReadSequence):

    def __iter__(self):
        # XXX not declared by IReadSequence,
        # dear zope.interface are you serious?!
        pass

    def create(target):
        """Returns a new IReference to the given ICMSContent object."""

    def get(target, default=None):
        """Returns IReference to the given target (uniqueId or ICMSContent)
        if one exists."""


class IXMLSource(zope.interface.Interface):
    """str representing the xml of an object."""


class IXMLContent(zeit.cms.repository.interfaces.IDAVContent,
                  IXMLRepresentation):
    """Content with an XML representation."""


class ITemplateManagerContainer(zope.container.interfaces.IReadContainer):
    """Container which holds all template managers."""


class ITemplateManager(zope.container.interfaces.IReadContainer):
    """Manages templates for a content type."""


class ITemplate(IXMLRepresentation):
    """A template for xml content types."""

    title = zope.schema.TextLine(title=_('Title'))


class IDAVPropertiesInXML(zope.interface.Interface):
    """Marker interface for objects which store their webdav properties in xml.

    It is common for articles and CPs to store their webdav properties in the
    xml, too. That is in addition to the Metadata stored as webdav properties.

    """


class IDAVPropertyXMLSynchroniser(zope.interface.Interface):
    """Synchronises dav properties to XML."""

    def set(namespace, name):
        """Set value for the DAV property (name, namespace)."""

    def sync():
        """Synchronise all properties."""


class ISynchronisingDAVPropertyToXMLEvent(zope.interface.Interface):

    namespace = zope.interface.Attribute("DAV property namespace")
    name = zope.interface.Attribute("DAV property name")
    value = zope.interface.Attribute("DAV property value")
    vetoed = zope.schema.Bool(
        title=u"True if sync was vetoed.",
        readonly=True,
        default=False)

    def veto():
        """Called by subscribers to veto the property being added to xml."""


class IAccessCounter(zope.interface.Interface):
    """Give information about how many times an object was accessed."""

    hits = zope.schema.Int(
        title=_('Hits today'),
        description=_('Indicates how many times a page viewed today.'),
        required=False,
        default=None)

    total_hits = zope.schema.Int(
        title=_('Total hits'),
        description=_('Indicates how many times a page was viewed in total, '
                      'i.e. during its entire life time.'),
        required=False,
        default=None)

    detail_url = zope.schema.URI(
        title=_('URI to the access counting details'),
        required=False,
        default=None)


class IContentSortKey(zope.interface.Interface):
    """Content objects can be adapted to this interface to get a sort key.

    The sort key usually is a tuple of (weight, lowercased-name)

    """


class ILivePropertyManager(zope.interface.Interface):
    """Manages live properties."""

    def register_live_property(name, namespace):
        """Register property as live property."""

    def unregister_live_property(name, namespace):
        """Unregister property as live property."""

    def is_live_property(name, namespace):
        """Return (bool) whether the property is a live property."""


class ISemanticChange(zope.interface.Interface):
    """Indicates when the content last changed meaningfully, as opposed to
    small corrections like fixed typos. This might be shown to the reader,
    e.g. as "Aktualisiert am" on article pages.
    """

    last_semantic_change = zope.schema.Datetime(
        title=_('Last semantic change'),
        required=False,
        readonly=True,
        default=None)

    has_semantic_change = zope.schema.Bool(
        title=_('Update last semantic change'),
        required=False,
        default=False)

    def update():
        """Set last semantic change to last modified."""


class IUUID(zope.interface.Interface):
    """Accessing the uuid of a content object."""

    id = zope.schema.ASCIILine(
        title=u"The uuid of the content object.",
        default=None,
        required=False)

    shortened = zope.schema.ASCIILine(
        title=u"id without `{urn:uuid:}` prefix",
        readonly=True,
        required=False,
        default=None)


class IMemo(zope.interface.Interface):
    """Provide a memo for additional remarks on a content object."""

    memo = zope.schema.Text(
        title=_('Memo'),
        required=False)


class IContentAdder(zope.interface.Interface):

    type_ = zope.schema.Choice(
        title=_("Type"),
        source=zeit.cms.content.sources.AddableCMSContentTypeSource())

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.RessortSource(),
        required=False)

    sub_ressort = zope.schema.Choice(
        title=_('Sub ressort'),
        source=zeit.cms.content.sources.SubRessortSource(),
        required=False)

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    month = zope.schema.Int(
        title=_("Month"),
        min=1,
        max=12)


class IAddLocation(zope.interface.Interface):
    """Marker interface that adapts a content type to a context object on which
    the add form should be displayed.

    Register this adapter for (content_type, IContentAdder), where content_type
    is an interface like ICMSContent or IImageGroup.
    """


class IAddableContent(zope.interface.interfaces.IInterface):
    """Interface type to register additional addable entries
    that are *not* ICMSContentTypes.
    """


class ISkipDefaultChannel(zope.interface.Interface):
    """Marker interface to opt out of setting default
    ICommonMetadata.channels according to ressort/sub_ressort."""


class ICachingTime(zope.interface.Interface):
    """Cacheing time interface for """

    browser = zope.schema.Int(
        title=_("Caching time browser"),
        min=0,
        max=3600,
        required=False)

    server = zope.schema.Int(
        title=_("Caching time server"),
        min=0,
        max=3600,
        required=False)
