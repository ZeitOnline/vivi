# :vim fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zeit.cms.content.field
from zeit.cms.content.interfaces import IXMLReference  # Backward compat.


class IEditableStructure(zope.interface.Interface):
    """Marker for (xml-) objects which have a zope schema."""


class IXInclude(IEditableStructure):
    """<xi:include>"""

    href = zope.schema.TextLine(
        title=u"Resource")

    fallback = zope.schema.TextLine(
        title=u"Alternativer Text",
        description=(u"Text, der angezeigt werden soll, wenn die Resource "
                     u"nicht eingebettet werden kann."),
        default=u"Das Ressort ist im Moment leider nicht erreichbar.")


class IBlock(IEditableStructure):
    """<block>"""

    priority = zope.schema.Int(
        title=u"Priorität",
        default=500,
        required=False)
    layout = zope.schema.TextLine(
        title=u"Layout",
        required=False)
    id = zope.schema.TextLine(
        title=u"Id",
        required=False)
    href = zope.schema.URI(
        title=u"URL/HREF",
        required=False)


class IText(IEditableStructure):

    text = zope.schema.Text(
        title=u"Text",
        required=False)


class IRaw(IEditableStructure):

    xml = zeit.cms.content.field.XMLTree(
        title=u"Raw")


class IContainer(IEditableStructure):
    """<column>"""

    label = zope.schema.TextLine(
        title=u"Label",
        required=False)
    style = zope.schema.TextLine(
        title=u"Style",
        required=False)
    layout = zope.schema.TextLine(
        title=u"Layout",
        required=False)


class IColumn(IEditableStructure):
    """<column>"""

    layout = zope.schema.TextLine(
        title=u"Layout",
        required=False)
