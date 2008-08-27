# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.schema

import zeit.cms.interfaces
import zeit.cms.content.field

from zeit.content.rawxml.i18n import MessageFactory as _


class IRawXML(zeit.cms.interfaces.IAsset):
    """An asset which is just raw xml."""

    title = zope.schema.TextLine(
        title=_('Title'))

    xml = zeit.cms.content.field.XMLTree(
        title=_('XML'))
