# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Hit counting."""

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _


class ICountStorage(zope.interface.Interface):
    """Central access to click counting.

    This utility takes care of refreshing and caching today.xml.

    """

    def get_count(unique_id):
        """Return access count for given unique id.

        returns amount of hits (int) or None if nothing is known about the
        given unique_id.

        """

    def get_count_date(unique_id):
        """Return the date when the sample was taken."""

    def __iter__():
        """Iterate over the stored unique_ids."""


LIFETIME_DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/lifetimecounter'


class ILifeTimeCounter(zope.interface.Interface):
    """Live time hit counter."""

    total_hits = zope.schema.Int(
        title=_('Total hits'),
        description=_('Total hits between first and last count.'))

    first_count = zope.schema.Date(
        title=_('Date the first hit was counted on'))

    last_count = zope.schema.Date(
        title=_('Date the last hit was counted on'))
