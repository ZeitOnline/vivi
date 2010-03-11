# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.interfaces
import zope.interface

ID_NAMESPACE = u'teasergroup://'


class ITeaserGroup(zeit.cms.interfaces.ICMSContent):

    name = zope.schema.TextLine(
        title=_('Name of teaser group'))

    teasers = zope.schema.Tuple(
        title=_('Linked teasers'),
        min_length=1,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))

    automatically_remove = zope.schema.Bool(
        title=_('Automatically remove'),
        default=True)


    def create():
        """Add the group to the database."""


class IRepository(zope.interface.Interface):
    """Repository for teaser groups."""

    def add(group):
        """Add teaser group.

        Adds given ITeaserGroup and assigns a unique id and __name__.

        """

    def __getitem__(name):
        """Get teaser group with given name."""
