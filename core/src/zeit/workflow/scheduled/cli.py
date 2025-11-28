import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload
import opentelemetry.trace
import pendulum
import zope.component

from zeit.cms.cli import commit_with_retry
from zeit.connector.models import ScheduledOperation
import zeit.cms.checkout.interfaces
import zeit.cms.cli
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.workflow.scheduled.interfaces


log = logging.getLogger(__name__)


class ScheduledOperationExecutor:
    def __init__(self):
        self.connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        self.repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        self.session = self.connector.session
        self.content = {}

    def execute_all(self):
        query_timeout = int(
            zeit.cms.config.get('zeit.workflow', 'scheduled-query-timeouts-ms', 10000)
        )
        query = (
            select(ScheduledOperation)
            .where(ScheduledOperation.scheduled_on <= pendulum.now('UTC'))
            .order_by(ScheduledOperation.scheduled_on)
            .options(joinedload(ScheduledOperation._content))
        )

        operations = list(self.connector.execute_sql(query, query_timeout).scalars())
        log.info('Found %d scheduled operations to execute', len(operations))
        self.content = {
            op.id: self.repository.getContent(op._content.uniqueid) for op in operations
        }

        for op in operations:
            for _ in commit_with_retry():
                try:
                    self._execute_operation(op)
                except Exception as e:
                    log.warning('Skip operation %s due to %s', op.id, e)
                    current_span = opentelemetry.trace.get_current_span()
                    current_span.record_exception(e)

    def _execute_operation(self, op):
        content = self.content.get(op.id, None)
        if not content:
            log.warning('Content not found for operation %s, deleting operation', op.id)
            self.session.delete(op)
            return

        log.info(
            'Executing %s operation for %s scheduled at %s',
            op.operation,
            content.uniqueId,
            op.scheduled_on,
        )

        self._apply_property_changes(content, op.property_changes)
        if op.operation == 'publish':
            self._execute_publish(content)
        elif op.operation == 'retract':
            self._execute_retract(content)
        else:
            # the forbidden route that we will never hit, I promise
            log.warning('Unknown operation type: %s', op.operation)

        self.session.delete(op)
        log.info('Successfully executed operation %s', op.id)

    def _get_content(self, op):
        """Get content object from operation."""
        try:
            if not op._content:
                return None

            uniqueid = op._content.uniqueid
            return self.repository.getContent(uniqueid)
        except Exception as e:
            log.warning('Error getting content for operation %s: %s', op.id, e)
            return None

    def _apply_property_changes(self, content, property_changes):
        if not property_changes:
            return

        try:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
            if manager.canCheckout:
                checked_out = manager.checkout()
            else:
                checked_out = content

            for prop_name, prop_value in property_changes.items():
                if hasattr(checked_out, prop_name):
                    old_value = getattr(checked_out, prop_name, None)
                    setattr(checked_out, prop_name, prop_value)
                    log.info(
                        'Changed %s.%s from %r to %r',
                        content.uniqueId,
                        prop_name,
                        old_value,
                        prop_value,
                    )
                else:
                    log.warning('Property %s not found on %s', prop_name, content.uniqueId)

            if manager.canCheckin:
                manager.checkin(checked_out)

        except Exception as e:
            log.error(
                'Error applying property changes to %s: %s', content.uniqueId, e, exc_info=True
            )
            raise

    def _execute_publish(self, content):
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        publish.publish(background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED)
        log.info('Published %s', content.uniqueId)

    def _execute_retract(self, content):
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if not info.published:
            log.info('Content %s already retracted, skipping', content.uniqueId)
            return

        publish = zeit.cms.workflow.interfaces.IPublish(content)
        publish.retract(background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED)
        log.info('Retracted %s', content.uniqueId)


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.workflow', 'schedule-principal'))
def execute_scheduled_operations_cli():
    executor = ScheduledOperationExecutor()
    executor.execute_all()
