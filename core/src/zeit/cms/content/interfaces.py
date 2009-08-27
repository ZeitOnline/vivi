# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component.interfaces
import zope.i18nmessageid
import zope.interface
import zope.interface.interfaces
import zope.schema

import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces

from zeit.cms.i18n import MessageFactory as _


# XXX There is too much, too unordered in here, clean this up.


class ICMSContentSource(zope.schema.interfaces.ISource):
    """A source for CMS content types."""


class INamedCMSContentSource(ICMSContentSource):
    """A source for CMS content which is registered as utility."""

    name = zope.interface.Attribute("Utility name of the source")

    def get_check_types():
        """Return a sequence of cms type identifiers which areincluded."""


class IKeywordInterface(zope.interface.interfaces.IInterface):
    """The interface of the keyword interface."""


class IKeyword(zope.interface.Interface):

    code = zope.schema.TextLine()
    label = zope.schema.TextLine()

    inTaxonomy = zope.schema.Bool(
        title=_("Keyword is contained in the taxonomy"),
        default=False)

IKeyword.narrower = zope.schema.List(value_type=zope.schema.Object(IKeyword))
IKeyword.broader = value_type=zope.schema.Object(IKeyword, required=False)


class IKeywords(zope.interface.Interface):

    root = zope.schema.Object(
        IKeyword,
        title=_('Root of ontology'))

    def __getitem__(code):
        """return IKeyword with given code."""

    def find_keywords(searchterm):
        """Returns a list of keywords which contain the searchterm
           string.
        """


class ICommonMetadata(zope.interface.Interface):

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53,
        required=False)

    page = zope.schema.Int(
        title=_("Page"),
        readonly=True,
        required=False)

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.NavigationSource())

    sub_ressort = zope.schema.Choice(
        title=_('Sub ressort'),
        source=zeit.cms.content.sources.SubNavigationSource(),
        required=False)

    printRessort = zope.schema.Choice(
        title=_("Print ressort"),
        source=zeit.cms.content.sources.PrintRessortSource(),
        readonly=True,
        required=False)

    authors = zope.schema.Tuple(
        title=_("Authors"),
        value_type=zope.schema.TextLine(),
        required=False,
        default=(u'',))

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=(),
        unique=True,
        value_type=zope.schema.Object(IKeyword))

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

    copyrights = zope.schema.TextLine(
        title=_("Copyright (c)"),
        description=_("Do not enter (c)."),
        default=u"ZEIT ONLINE")

    supertitle = zope.schema.TextLine(
        title=_("Kicker"),
        description=_("Please take care of capitalisation."),
        required=False)

    byline = zope.schema.TextLine(
        title=_("By line"),
        required=False)

    title = zeit.cms.content.field.XMLSnippet(
        title=_("Title"))

    subtitle = zeit.cms.content.field.XMLSnippet(
        title=_("Subtitle"),
        required=False)

    teaserTitle = zope.schema.Text(
        title=_("Teaser title"),
        required=False)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    shortTeaserTitle = zope.schema.Text(
        title=_("Index teaser title"),
        required=False,
        max_length=20)

    shortTeaserText = zope.schema.Text(
        title=_("Index teaser text"),
        required=False,
        max_length=50)

    hpTeaserTitle = zope.schema.Text(
        title=_('Homepage teaser title'),
        required=False)

    hpTeaserText = zope.schema.Text(
        title=_('Homepage teaser text'),
        required=False)


    vg_wort_id = zope.schema.TextLine(
        title=_('VG Wort Id'),
        required=False)

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily newsletter"),
        description=_(
            "Should this article be listed in the daily newsletter?"),
        default=True)

    commentsAllowed = zope.schema.Bool(
        title=_("Comments allowed"),
        default=True)

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=True)

    banner_id = zope.schema.TextLine(
        title=_('Banner id'),
        required=False)

    product_id = zope.schema.Choice(
        title=_('Product id'),
        default='ZEDE',
        source=zeit.cms.content.sources.ProductSource())

    product_text = zope.interface.Attribute(
        "Title of product_id (r/o).")

    foldable = zope.schema.Bool(
        title=_('Foldable'),
        default=True)

    minimal_header = zope.schema.Bool(
        title=_('Minimal header'))

    sub_type = zope.schema.Choice(
        title=_('Sub type'),
        values=(u'Arena', u'Frame', u'Template', u'Iframe'),
        required=False)

    color_scheme = zope.schema.Choice(
        title=_('Color scheme'),
        values=(u'Redaktion', u'Verlag'),
        default=u'Redaktion')


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


class IDAVPropertyChangedEvent(zope.component.interfaces.IObjectEvent):
    """A dav property has been changed."""

    old_value = zope.interface.Attribute("The value before the change.")
    new_value = zope.interface.Attribute("The value after the change.")

    property_namespace = zope.interface.Attribute("Webdav property namespace.")
    property_name = zope.interface.Attribute("Webdav property name.")

    field = zope.interface.Attribute(
        "zope.schema field the property was changed for.")


class DAVPropertyChangedEvent(zope.component.interfaces.ObjectEvent):
    zope.interface.implements(IDAVPropertyChangedEvent)

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

    Object references are dependent on the target object. For instance a feed
    is referenced with <xi:include> while an image is referenced using <img>.

    Adapting to IXMLReference yields an lxml.objectify tree
    """


class IXMLReferenceUpdater(zope.interface.Interface):
    """Objects that update metadata etc on XML references."""

    def update(xml_node):
        """Update xml_node with data from the content object.

        xml_node: lxml.objectify'ed element

        """


class IXMLSource(zope.interface.Interface):
    """str representing the xml of an object."""


class IXMLContent(zeit.cms.interfaces.ICMSContent, IXMLRepresentation):
    """Content with an XML representation."""


class ITemplateManagerContainer(zope.app.container.interfaces.IReadContainer):
    """Container which holds all template managers."""


class ITemplateManager(zope.app.container.interfaces.IReadContainer):
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


class IContentSortKey(zope.interface.Interface):
    """Content objects can be adapted to this interface to get a sort key.

    The sort key usually is a tuple of (weight, lowercased-name)

    """


class ILivePropertyManager(zope.interface.Interface):
    """Manages live properties."""

    def register_live_property(name, namespace):
        """Register property as live property."""

    def is_live_property(name, namespace):
        """Return (bool) whether the property is a live property."""


class ISemanticChange(zope.interface.Interface):

    last_semantic_change = zope.schema.Datetime(
        title=_('Last semantic change'),
        required=False,
        readonly=True,
        default=None)


class IUUID(zope.interface.Interface):
    """Accessing the uuid of a content object."""

    id = zope.schema.ASCIILine(
            title=u"The uuid of the content object.",
            default=None,
            required=False)
