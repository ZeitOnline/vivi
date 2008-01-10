# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component.interfaces
import zope.interface
import zope.schema


FEED_NAMESPACE = u'http://namespaces.zeit.de/CMS/feed'


class ISyndicationManager(zope.interface.Interface):
    """Manages syndication of a content object."""

    targets = zope.interface.Attribute("List possible syndication targets.")

    canSyndicate = zope.interface.Attribute(
        "True if the object can be syndicated; False otherwise.")

    def syndicate(targets):
        """Syndicate the managed object to the given targets.

        raises SyndicationError if the object could not be syndicated.

        """


class IReadFeed(zope.interface.Interface):
    """Feed read interface."""

    title = zope.schema.TextLine(title=u"Title")
    object_limit = zope.schema.Int(
        title=u"Anzahl begrenzen",
        description=(u"Begrenzt die Anzahl der Objekte im Feed auf die "
                     u"angegebene Anzahl. Beim Syndizieren eines neuen "
                     u"Objekts wird das letzte aus dem Feed entfernt."),
        default=50,
        min=1,
        required=False)

    def pinned(content):
        """Returns true, if content is pinned"""

    def __len__():
        """Return amount of objects syndicated."""

    def __iter__():
        """Iterate over published content.

        When content is pinned __iter__ is supposed to return pinned content
        at the right position.

        """

    def getPosition(content):
        """Returns the position of `content` in the feed.

        Returns 1-based position of the content object in the feed or None if
        the content is not syndicated in this feed.

        """


class IWriteFeed(zope.interface.Interface):
    """Feed write interface."""

    def insert(index, content):
        """Add `content` to self at position `index`."""

    def remove(content):
        """Remove `content` from feed."""

    def pin(content):
        """Pin `content` to current position."""

    def unpin(content):
        """Remove pining for `content`. """

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is a list or a tuple containing the set of existing keys in
        the new order. `order` must contain ``len(keys())`` items and cannot
        contain duplicate keys.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """

    def updateMetadata(self, content):
        """Update the metadata of a contained object.

        Raises KeyError if the content is not syndicated in this feed.

        """

class IFeed(IReadFeed, IWriteFeed):
    """Documents can be published into a feed."""


class IContentSyndicatedEvent(zope.component.interfaces.IObjectEvent):
    """Issued when an object is syndicated."""

    targets = zope.schema.Set(
        title=u"The syndication target.",
        value_type=zope.schema.Object(IFeed))


class ContentSyndicatedEvent(zope.component.interfaces.ObjectEvent):
    """Issued when an object is syndicated."""

    zope.interface.implements(IContentSyndicatedEvent)

    def __init__(self, object, targets):
        super(ContentSyndicatedEvent, self).__init__(object)
        self.targets = set(targets)


class SyndicationError(Exception):
    """Raised when there is an error during syndication."""


class IMySyndicationTargets(zope.interface.Interface):

    targets = zope.schema.Tuple(
        title=u"Syndizierungsziele",
        default=(),
        required=False,
        value_type=zope.schema.Object(IFeed))


class IFeedMetadataUpdater(zope.interface.Interface):
    """Update feed entry metadata.
    """

    def update_entry(entry, obj):
        """Update entry with data from obj.

        Entry: lxml.objectify'ed element from the feed.
        obj: the object to be updated.

        """
