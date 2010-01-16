# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Centerpage interfaces."""

import copy
import zope.schema

import zeit.cms.interfaces
import zeit.cms.content.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.xmleditor.interfaces


class ICenterPageMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Cennter page metadata."""

    year = copy.copy(zeit.cms.content.interfaces.ICommonMetadata['year'])
    year.required = False

    volume = copy.copy(zeit.cms.content.interfaces.ICommonMetadata['volume'])
    volume.required = False


class ICenterPage(ICenterPageMetadata,
                  zeit.cms.content.interfaces.IXMLContent):
    """A center page"""


class IContainer(zeit.xmleditor.interfaces.IEditableStructure):
    """<column>"""

    label = zope.schema.TextLine(
        title=_("Label"),
        required=False)
    style = zope.schema.TextLine(
        title=_("Style"),
        required=False)
    layout = zope.schema.TextLine(
        title=_("Layout"),
        required=False)


class IColumn(zeit.xmleditor.interfaces.IEditableStructure):
    """<column>"""

    layout = zope.schema.TextLine(
        title=_("Layout"),
        required=False)
