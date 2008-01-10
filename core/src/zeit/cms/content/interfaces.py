# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component.interfaces
import zope.i18nmessageid
import zope.interface
import zope.interface.interfaces
import zope.schema.interfaces

import zope.app.locking.interfaces

import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


class IXMLTreeWidget(zope.app.form.browser.interfaces.ITextBrowserWidget):
    """A widget for source editing xml trees."""


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


class ICommonMetadata(zope.interface.Interface):

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53)

    page = zope.schema.Int(
        title=_("Page"),
        readonly=True,
        required=False)

    ressort = zope.schema.TextLine(
        title=_("Ressort"),
        default=u"Online",
        readonly=True,
        required=True)

    authors = zope.schema.Tuple(
        title=_("Authors"),
        value_type=zope.schema.TextLine(),
        required=False,
        default=())

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=(),
        value_type=zope.schema.Object(IKeyword))

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

    copyrights = zope.schema.TextLine(
        title=_("Copyright"),
        description=_("Do not enter (c)."),
        default=u"ZEIT online")

    supertitle = zope.schema.TextLine(
        title=_("Kicker"),
        description=_("Please take care of capiltalisation."),
        required=False)

    byline = zope.schema.TextLine(
        title=_("By line"),
        required=False)

    title = zope.schema.TextLine(
        title=_("Title"))

    subtitle = zope.schema.Text(
        title=_("Subtitle"),
        required=False)

    teaserTitle = zope.schema.Text(
        title=_("Teaser titel"),
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


class IFromProperty(zope.interface.Interface):
    """Parse a unicode string from a DAV property to a value."""

    def fromProperty(value):
        """Convert property value to python value.

        returns python object represented by value.

        raises ValueError if the value could not be converted.
        raises zope.schema.ValidationError if the value could be converted but
        does not satisfy the constraints.

        """


class IToProperty(zope.interface.Interface):
    """Serlalize value to DAV property value."""

    def toProperty(value):
        """Convert python value to DAV property value.

        returns unicode
        """

class IDAVToken(zope.interface.Interface):
    """A string representing a token that uniquely identifies a value."""


class IDAVPropertyChangedEvent(zope.component.interfaces.IObjectEvent):
    """A dav property has been changed."""

    old_value = zope.interface.Attribute("The value before the change.")
    new_value = zope.interface.Attribute("The value after the change.")

    property_namespace = zope.interface.Attribute("Webdav property namespace.")
    property_name = zope.interface.Attribute("Webdav property name.")


class DAVPropertyChangedEvent(zope.component.interfaces.ObjectEvent):
    zope.interface.implements(IDAVPropertyChangedEvent)

    def __init__(self, object, property_namespace, property_name,
                 old_value, new_value):
        self.object = object
        self.property_namespace = property_namespace
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value


class ITextContent(zeit.cms.interfaces.ICMSContent):
    """Representing text content XXX"""

    data = zope.schema.Text(title=u"Document content")


class IXMLRepresentation(zope.interface.Interface):
    """Objects with an XML representation."""

    xml = zeit.cms.content.field.XMLTree(
        title=_("XML Source"))


class IXMLSource(zope.interface.Interface):
    """str representing the xml of an object."""


class IXMLContent(zeit.cms.interfaces.ICMSContent, IXMLRepresentation):
    """Content with an XML representation.

    Usually *all* data should be stored in the XML structure *or* in
    webdav properties.

    """

    properties = zope.schema.Object(zeit.cms.interfaces.IWebDAVProperties)


class ILockInfo(zope.app.locking.interfaces.ILockInfo):
    """Extended LockInfo interface."""

    locked_until = zope.schema.Datetime(
        title=u"Locked Until",
        required=False)


class ITemplateManager(zope.app.container.interfaces.IReadContainer):
    """Manages templates for a content type."""


class ITemplate(IXMLRepresentation):
    """A template for xml content types."""

    title = zope.schema.TextLine(title=_('Title'))


class ICMSContentSource(zope.schema.interfaces.ISource):
    """A source for CMS content types."""

    name = zope.interface.Attribute(
        "Utility name of the source")
