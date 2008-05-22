# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging

import zope.component

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.relation.interfaces

logger = logging.getLogger(__name__)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def updateFeedOnCheckin(context, event):
    """Update metadata in feed on checkin of objects."""
    auto = zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate(
        context, None)
    if auto is None:
        logger.debug("No automatic update of metadata for %s because"
                     "no IAutomaticMetadataUpdate adapter found." %(
                         context.uniqueId,))
        return

    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    syndicated_in = relations.get_relations(context, 'syndicated_in')

    updateable_feeds = set(syndicated_in).difference(
        auto.automaticMetadataUpdateDisabled)

    checked_out = []

    for feed in updateable_feeds:
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(feed)
        try:
            co_feed = manager.checkout(event=False)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError, e:
            # Ignore this channel.
            logger.error("Could not update channel %s after checkin of %s: "
                         "%s: %s" % (
                             feed.uniqueId, context.uniqueId,
                             e.__class__.__name__, e.args))
            continue
        checked_out.append(co_feed)

    for feed in checked_out:
        feed.updateMetadata(context)

    # Everything is checked out and updated now. Check back in.
    for feed in checked_out:
        manager = zeit.cms.checkout.interfaces.ICheckinManager(feed)
        try:
            manager.checkin(event=False)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # Leave object checked out. And continue with the others.
            pass
