"""Event handlers for syncing scheduled operations between ZODB and SQL."""

import logging

import grokcore.component as grok

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.workflow.scheduled.operations import IScheduledOperations
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces


log = logging.getLogger(__name__)


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def copy_operations_to_workingcopy(context, event):
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        return

    if not FEATURE_TOGGLES.find('use_scheduled_operations'):
        return

    content_id = zeit.cms.content.interfaces.IUUID(context).shortened
    if not content_id:
        return

    repository = IScheduledOperations(zeit.cms.interfaces.ICMSContent(context.uniqueId))
    workingcopy = IScheduledOperations(context)
    workingcopy.synchronize(repository.list())


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def sync_operations_to_repository(context, event):
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        return

    if not FEATURE_TOGGLES.find('use_scheduled_operations'):
        return

    content_id = zeit.cms.content.interfaces.IUUID(context).shortened
    if not content_id:
        return

    repository = IScheduledOperations(zeit.cms.interfaces.ICMSContent(context.uniqueId))
    workingcopy = IScheduledOperations(context)

    repository.synchronize(workingcopy.list())
