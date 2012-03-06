# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
from zeit.cms.i18n import MessageFactory as _
import logging
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.workflow.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.component
import zope.event
import zope.interface
import zope.location.location


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS
logger = logging.getLogger(__name__)


class ContentWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    """Adapt ICMSContent to IWorkflow using the "live" data from connector.

    We must read and write properties directly from the DAV to be sure we
    actually can do the transition.
    """

    zope.interface.implements(zeit.workflow.interfaces.IContentWorkflow)
    zope.component.adapts(zeit.cms.interfaces.IEditorialContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IContentWorkflow,
        WORKFLOW_NS,
        ('edited', 'corrected', 'refined', 'images_added', 'urgent'),
        live=True)

    def can_publish(self):
        if self.urgent:
            return True
        if all([self.edited, self.corrected, self.refined, self.images_added]):
            return True
        return False


@zope.component.adapter(
    zeit.workflow.interfaces.IContentWorkflow,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def log_workflow_changes(workflow, event):
    if event.field.__name__ not in ('edited', 'corrected', 'refined',
                                    'images_added', 'urgent'):
        # Only act on certain fields.
        return

    content = workflow.context
    message = _('${name}: ${new_value}',
                mapping=dict(name=event.field.title,
                             old_value=event.old_value,
                             new_value=event.new_value))

    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    log.log(content, message)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.workflow.interfaces.IRetractedEvent)
def remove_from_channels_after_retract(context, event):
    """Removes objects from channels when they're retracted."""
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    syndicated_in = relations.get_relations(context)
    for feed in list(syndicated_in):
        # XXX we might want to store the kind of relation
        if not zeit.cms.syndication.interfaces.IFeed.providedBy(feed):
            continue
        with zeit.cms.checkout.helper.checked_out(feed) as checked_out:
            if checked_out is not None:
                try:
                    checked_out.remove(context)
                except ValueError:
                    # Was not in the feed, i.e. the index wasn't up to date.
                    # Ignore.
                    pass
