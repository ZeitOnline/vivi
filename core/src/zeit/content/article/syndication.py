# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import iso8601
import lxml.objectify
import pytz

import zope.component
import zope.interface

import zeit.cms.checkout.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.article.interfaces


class SyndicationEventLog(object):

    zope.interface.implements(
        zeit.content.article.interfaces.ISyndicationEventLog)

    def __init__(self, syndicated_in, syndicated_on=None):
        self.syndicatedIn = frozenset(syndicated_in)
        if syndicated_on is None:
            self.syndicatedOn = datetime.datetime.now(pytz.UTC)
        else:
            self.syndicatedOn = syndicated_on


class SyndicationLogProperty(zeit.cms.content.property.MultiPropertyBase):

    def __init__(self):
        super(SyndicationLogProperty, self).__init__(
            '.head.syndicationlog.entry')

    def _element_factory(self, node, tree):
        repository = self.repository
        syndicated_on = iso8601.parse_date(unicode(node.syndicatedOn))
        syndicated_in = []
        for unique_id in node.syndicatedIn:
            unique_id = unicode(unique_id)
            syndicated_in.append(repository.getContent(unique_id))
        return SyndicationEventLog(syndicated_in, syndicated_on)

    def _node_factory(self, entry, tree):
        node = tree.makeelement('entry')
        node.syndicatedOn = entry.syndicatedOn
        node.syndicatedIn = [feed.uniqueId for feed in entry.syndicatedIn]
        return node

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.syndication.interfaces.IContentSyndicatedEvent)
def linkToFeed(object, event):
    """Link from the article to the feeds in event."""

    new_syndicated_in = object.syndicatedIn | event.targets
    new_auto_sync = object.automaticTeaserSyndication | event.targets

    if (new_syndicated_in == object.syndicatedIn and
        new_auto_sync == object.automaticTeaserSyndication):
        # All feeds are noted in the article already, do nothing
        return

    manager = zeit.cms.checkout.interfaces.ICheckoutManager(object)
    try:
        checked_out = manager.checkout(event=False)
    except zeit.cms.checkout.interfaces.CheckinCheckoutError:
        raise zeit.cms.syndication.interfaces.SyndicationError(
            "Cannot lock %r. Syndication not possible right now." %
            object.uniqueId)

    checked_out.syndicatedIn = new_syndicated_in
    checked_out.automaticTeaserSyndication = new_auto_sync
    checked_out.syndicationLog += (SyndicationEventLog(event.targets), )

    manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
    manager.checkin(event=False)


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def updateFeedOnCheckin(object, event):
    updateable_feeds = object.automaticTeaserSyndication
    checked_out = []

    for feed in updateable_feeds:
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(feed)
        try:
            co_feed = manager.checkout(event=False)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # TODO: throw away checked_out
            raise zeit.cms.syndication.interfaces.SyndicationError(
                "Could not checkout %r." % feed.uniqueId)
        checked_out.append(co_feed)

    for feed in checked_out:
        feed.updateMetadata(object)

    # Everything is checked out and updated now. Check back in.
    for feed in checked_out:
        manager = zeit.cms.checkout.interfaces.ICheckinManager(feed)
        try:
            manager.checkin(event=False)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # Leave object checked out. And continue with the others.
            pass
