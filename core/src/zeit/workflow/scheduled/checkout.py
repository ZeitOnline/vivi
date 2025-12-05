"""Event handlers for syncing scheduled operations between ZODB and SQL.

Lifecycle:
- AfterCheckout: Copy operations from SQL to ZODB
- BeforeCheckin: Sync operations from ZODB to SQL
- BeforeDelete: Discard ZODB operations
"""

import logging

import grokcore.component as grok

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.workflow.scheduled.operations import (
    SQLScheduledOperationsStorage,
    ZODBScheduledOperationsStorage,
)
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

    sql_storage = SQLScheduledOperationsStorage(context)
    sql_operations = sql_storage.list()

    if not sql_operations:
        log.debug('AfterCheckout: no operations to copy for %s', context.uniqueId)
        return

    zodb_storage = ZODBScheduledOperationsStorage(context)
    for sql_op in sql_operations:
        zodb_storage.add(
            operation_id=sql_op.id,
            operation=sql_op.operation,
            scheduled_on=sql_op.scheduled_on,
            property_changes=sql_op.property_changes,
            created_by=sql_op.created_by,
            date_created=sql_op.date_created,
        )

    log.debug(
        'AfterCheckout: copied %d operation(s) from SQL to ZODB for %s',
        len(sql_operations),
        context.uniqueId,
    )


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def sync_operations_to_repository(context, event):
    """Replaces all SQL operations with current ZODB state (delete + insert),
    because simpler and because we do not have that many operations performance
    impact should be negligible.
    """
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        return

    if not FEATURE_TOGGLES.find('use_scheduled_operations'):
        return

    content_id = zeit.cms.content.interfaces.IUUID(context).shortened
    if not content_id:
        return

    zodb_storage = ZODBScheduledOperationsStorage(context)
    zodb_operations = zodb_storage.list()

    log.debug(
        'BeforeCheckin: syncing %d operation(s) from ZODB to SQL for %s',
        len(zodb_operations),
        context.uniqueId,
    )

    sql_storage = SQLScheduledOperationsStorage(context)

    sql_operations = sql_storage.list()
    for sql_op in sql_operations:
        sql_storage.remove(sql_op.id)

    for zodb_op in zodb_operations:
        sql_storage.add(
            operation_id=zodb_op.id,
            operation=zodb_op.operation,
            scheduled_on=zodb_op.scheduled_on,
            property_changes=zodb_op.property_changes,
            created_by=zodb_op.created_by,
            date_created=zodb_op.date_created,
        )

    log.debug(
        'BeforeCheckin: synced %d operation(s) for %s', len(zodb_operations), context.uniqueId
    )


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IBeforeDeleteEvent)
def discard_working_copy_operations(context, event):
    """ZODB transaction rollback automatically discards the data."""
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        return

    zodb_storage = ZODBScheduledOperationsStorage(context)
    zodb_operations = zodb_storage.list()

    if zodb_operations:
        log.debug(
            'BeforeDelete: discarding %d operation(s) from ZODB for %s',
            len(zodb_operations),
            context.uniqueId,
        )
