# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema

import zeit.cms.interfaces
import zeit.cms.content.interfaces

import zeit.xmleditor.interfaces


class ICenterPageMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Cennter page metadata."""

class ICenterPage(ICenterPageMetadata,
                  zeit.cms.content.interfaces.IXMLContent):
    """A center page"""


class IContainer(zeit.xmleditor.interfaces.IEditableStructure):
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


class IColumn(zeit.xmleditor.interfaces.IEditableStructure):
    """<column>"""

    layout = zope.schema.TextLine(
        title=u"Layout",
        required=False)
