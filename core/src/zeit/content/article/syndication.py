# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zeit.cms.checkout.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.article.interfaces


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

    manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
    manager.checkin(event=False)


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.ICheckinEvent)
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
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(feed)
        try:
            manager.checkin(event=False)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # Leave object checked out. And continue with the others.
            pass
