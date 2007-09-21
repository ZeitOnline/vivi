# vim:fileencoding=utf-8 encoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component.interfaces
import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces

import zope.app.locking.interfaces

import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


class IXMLTreeWidget(zope.app.form.browser.interfaces.ITextBrowserWidget):
    """A widget for source editing xml trees."""


class ICommonMetadata(zope.interface.Interface):

    year = zope.schema.Int(
        title=_("Jahr"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Ausgabe"),
        min=1,
        max=53)

    page = zope.schema.Int(
        title=_("Seite"),
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
        value_type=zope.schema.TextLine())

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

    copyrights = zope.schema.TextLine(
        title=_("copyright"),
        description=_("Do not enter (c)."),
        default=u"ZEIT online")

    supertitle = zope.schema.TextLine(
        title=_("Spitzmarke"),
        description=_("Case sensitive."),
        required=False)

    byline = zope.schema.TextLine(
        title=_("By line"),
        required=False)

    title = zope.schema.TextLine(
        title=_("Titel"))

    subtitle = zope.schema.TextLine(
        title=_("Untertitel"),
        required=False)

    teaserTitle = zope.schema.TextLine(
        title=_("Teaser titel"),
        required=False)

    teaserText = zope.schema.TextLine(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    shortTeaserTitle = zope.schema.TextLine(
        title=_("Index teaser title"),
        required=False,
        max_length=20)

    shortTeaserText = zope.schema.TextLine(
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
    xml_source = zope.interface.Attribute(
        "XML source (str, *not* unicode) representing the object.")


class IXMLContent(zeit.cms.interfaces.ICMSContent, IXMLRepresentation):
    """Content with an XML representation.

    Usually *all* data should be stored in the XML structure *or* in
    webdav properties.

    """

    properties = zope.schema.Object(zeit.cms.interfaces.IWebDAVProperties)


class ITeaser(zope.interface.Interface):
    """A teaser is a brief introduction to an article or other document."""

    title = zope.schema.TextLine(title=_('Teaser Title'))
    text = zope.schema.TextLine(title=_('Teaser Text'),
                                max_length=170)


class IIndexTeaser(zope.interface.Interface):
    """An index teaser is a *very* short in troduction to a document."""

    title = zope.schema.TextLine(title=_('Index Teaser Title'),
                                 max_length=20)
    text = zope.schema.TextLine(title=_('Index Teaser Text'),
                                max_length=50)


class ILockInfo(zope.app.locking.interfaces.ILockInfo):
    """Extended LockInfo interface."""

    locked_until = zope.schema.Datetime(
        title=u"Locked Until",
        required=False)


class IKeyword(zope.interface.Interface):


    code = zope.schema.TextLine()
    label = zope.schema.TextLine()

IKeyword.narrower = zope.schema.List(value_type=zope.schema.Object(IKeyword))
IKeyword.broader = value_type=zope.schema.Object(IKeyword, required=False)
