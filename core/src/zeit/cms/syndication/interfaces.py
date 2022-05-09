import zope.component
import zope.interface
import zope.schema

import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.relation.interfaces
from zeit.cms.i18n import MessageFactory as _


class ISyndicationManager(zope.interface.Interface):
    """Manages syndication of a content object."""

    targets = zope.interface.Attribute("List possible syndication targets.")

    canSyndicate = zope.interface.Attribute(
        "True if the object can be syndicated; False otherwise.")

    def syndicate(targets):
        """Syndicate the managed object to the given targets.

        raises SyndicationError if the object could not be syndicated.

        """


class IEntry(zope.interface.Interface):
    """An entry in a feed."""

    pinned = zope.schema.Bool(
        title=_('Pinned'))

    hidden = zope.schema.Bool(
        title=_('Hidden on HP'))

    big_layout = zope.schema.Bool(
        title=_('Big layout'))

    hidden_relateds = zope.schema.Bool(
        title=_('Hidden relateds'))


class IReadFeed(zope.interface.Interface):
    """Feed read interface."""

    title = zope.schema.TextLine(title=_("Title"))
    object_limit = zope.schema.Int(
        title=_("Limit amount"),
        description=_("limit-amount-description"),
        default=50,
        min=1,
        required=False)

    def __len__():
        """Return amount of objects syndicated."""

    def __iter__():
        """Iterate over published content.

        When content is pinned __iter__ is supposed to return pinned content
        at the right position.

        """

    def __contains__(content):
        """Return if content is syndicated in this channel."""

    def getPosition(content):
        """Returns the position of `content` in the feed.

        Returns 1-based position of the content object in the feed or None if
        the content is not syndicated in this feed.

        """

    def getMetadata(content):
        """Returns IEntry instance corresponding to content."""


class IWriteFeed(zope.interface.Interface):
    """Feed write interface."""

    def insert(position, content):
        """Add `content` to self at position `position`."""

    def append(content):
        """Add `content` to self at end."""

    def remove(content):
        """Remove `content` from feed.

        raises ValueError if `content` not in feed.

        """

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is a list or a tuple containing the set of existing keys in
        the new order. `order` must contain ``len(keys())`` items and cannot
        contain duplicate keys.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """

    def updateMetadata(content):
        """Update the metadata of a contained object.

        Raises KeyError if the content is not syndicated in this feed.

        """


class IFeed(IReadFeed, IWriteFeed):
    """Documents can be published into a feed."""


class IContentSyndicatedEvent(zope.interface.interfaces.IObjectEvent):
    """Issued when an object is syndicated."""

    targets = zope.schema.Set(
        title='The syndication target.',
        value_type=zope.schema.Object(IFeed))


@zope.interface.implementer(IContentSyndicatedEvent)
class ContentSyndicatedEvent(zope.interface.interfaces.ObjectEvent):
    """Issued when an object is syndicated."""

    def __init__(self, object, targets):
        super().__init__(object)
        self.targets = set(targets)


class SyndicationError(Exception):
    """Raised when there is an error during syndication."""


class IMySyndicationTargets(zope.interface.Interface):

    def add(feed):
        """Add feed to my targets."""

    def remove(feed):
        """Remove feed from my targets."""

    def __contains__(feed):
        """Return (bool) whether feed is a target or not."""

    def __iter__():
        """Iterate over targets."""


class IFeedSource(zeit.cms.content.interfaces.ICMSContentSource):
    """A source for feeds."""


@zope.interface.implementer(IFeedSource)
class FeedSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.cms.syndication.feed'
    check_interfaces = (IFeed,)


feedSource = FeedSource()
