# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.rawxml.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.schema


class IRawXML(zeit.cms.interfaces.IAsset,
              zeit.cms.content.interfaces.IXMLRepresentation,
              zeit.cms.repository.interfaces.IDAVContent):
    """An asset which is just raw xml."""

    title = zope.schema.TextLine(
        title=_('Title'))

    omitRootOnSyndicate = zope.schema.Bool(
        title=_('Omit root node when syndicting'),
        description=_('omitRootOnSyndicate-description'))
