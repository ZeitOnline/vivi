# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging

import zope.component

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.relation.corehandlers


log = logging.getLogger(__name__)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def updateFeedOnCheckin(context, event):
    """Update metadata in feed on checkin of objects."""
    auto = zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate(
        context, None)
    if auto is None:
        log.debug("No automatic update of metadata for %s because"
                  "no IAutomaticMetadataUpdate adapter found." %(
                      context.uniqueId,))
        return

    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    syndicated_in = relations.get_relations(context, 'syndicated_in')

    updateable_feeds = set(syndicated_in).difference(
        auto.automaticMetadataUpdateDisabled)

    def update_feed_metadata(checked_out_feed):
        try:
            checked_out_feed.updateMetadata(context)
        except KeyError:
            # Hum. The context wasn't in the feed actually. Well, after the
            # checkin the index will be upated.
            pass
        return True  # Assume feed always changes.

    for feed in updateable_feeds:
        zeit.cms.relation.corehandlers.with_checked_out(
            feed, update_feed_metadata, events=False)
