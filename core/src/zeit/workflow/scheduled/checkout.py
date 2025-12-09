"""Event handlers for syncing scheduled operations between ZODB and SQL."""

import logging

import grokcore.component as grok
import pendulum
import zope.lifecycleevent

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.workflow.scheduled.operations import IScheduledOperations
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.workflow.interfaces


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


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zope.lifecycleevent.IObjectAddedEvent)
def create_operations_from_release_period(context, event):
    """Handles the case where content is created with release_period set
    (e.g. from newsimport or brightcove) but doesn't have a persisted UUID yet.
    """
    if not FEATURE_TOGGLES.find('use_scheduled_operations'):
        return
    if zeit.cms.repository.interfaces.IRepository.providedBy(context):
        return
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(event.newParent):
        return

    # reload to get content from db for the uuid
    content = zeit.cms.interfaces.ICMSContent(context.uniqueId)
    content_id = zeit.cms.content.interfaces.IUUID(content, None)
    if content_id is None or not content_id.shortened:
        return

    timebased = zeit.workflow.interfaces.ITimeBasedPublishing(content, None)
    if timebased is None:
        return

    released_from, released_to = timebased.release_period or (None, None)

    ops = IScheduledOperations(content)

    publish_op = next((op for op in ops.list('publish') if not op.property_changes), None)
    retract_op = next((op for op in ops.list('retract') if not op.property_changes), None)

    if released_from is not None and released_from >= pendulum.now('UTC'):
        if publish_op:
            ops.update(publish_op.id, scheduled_on=released_from)
            log.info(
                'Updated scheduled publish operation %s from released_from for %s',
                publish_op.id,
                content.uniqueId,
            )
        else:
            op_id = ops.add('publish', released_from)
            log.info(
                'Created scheduled publish operation %s from released_from for %s',
                op_id,
                content.uniqueId,
            )
    elif publish_op:
        ops.remove(publish_op.id)
        log.info(
            'Removed scheduled publish operation %s (released_from cleared) for %s',
            publish_op.id,
            content.uniqueId,
        )

    if released_to is not None and released_to >= pendulum.now('UTC'):
        if retract_op:
            ops.update(retract_op.id, scheduled_on=released_to)
            log.info(
                'Updated scheduled retract operation %s from released_to for %s',
                retract_op.id,
                content.uniqueId,
            )
        else:
            op_id = ops.add('retract', released_to)
            log.info(
                'Created scheduled retract operation %s from released_to for %s',
                op_id,
                content.uniqueId,
            )
    elif retract_op:
        ops.remove(retract_op.id)
        log.info(
            'Removed scheduled retract operation %s (released_to cleared) for %s',
            retract_op.id,
            content.uniqueId,
        )
