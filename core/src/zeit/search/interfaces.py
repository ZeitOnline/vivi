# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.i18nmessageid
import zope.interface
import zope.schema

_ = zope.i18nmessageid.MessageFactory('zeit.cms')


class ISearchResult(zope.interface.Interface):
    """Represents one item in a list of results."""

    uniqueId = zope.schema.TextLine(title=_("Unique Id"), readonly=True)
    __name__ = zope.schema.TextLine(title=_("File name"))

    title = zope.schema.TextLine(title=_('Title'))
    author = zope.schema.TextLine(title=_('Author'))

    year = zope.schema.Int(title=_('Year'))
    volume = zope.schema.Int(title=_('Volume'))
    page = zope.schema.Int(title=_('Page'))

    weight = zope.schema.Int(title=_(
        'Realive weight of metadata freshness.'))

    relevance = zope.schema.Int(
        title=_('Relevance of result'))


class ISearchInterface(zope.interface.Interface):
    """Defines a very easy interface for search."""

    indexes = zope.schema.Set(title=u"Supported indexes")

    def __call__(**kwargs):
        """Search for documents specified by kwargs.

        Key: index to search
        Value: value to search for

        If key is not in indexes the key is ignored.

        returns a sequence of ISearchResult instances with metadata filled as
        available.

        """

class ISearch(zope.interface.Interface):
    """Search via ISearchInterface utilities.

    Queries registered search interfaces and combines results.

    """

    def __call__(**kwargs):
        """Search for documents specified by kwargs."""
