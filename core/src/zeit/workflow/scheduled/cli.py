import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload
import opentelemetry.trace
import pendulum
import zope.component

from zeit.cms.cli import commit_with_retry
from zeit.cms.i18n import MessageFactory as msg
from zeit.connector.models import ScheduledOperation
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.workflow.scheduled.interfaces


log = logging.getLogger(__name__)


class ScheduledOperationProcessor:
    def __init__(self):
        self.connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        self.repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        self.session = self.connector.session
        self.objectlog = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)

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
        log.debug('Found %d scheduled operations to execute', len(operations))

        # Objects are getting detached, because of a transaction boundary somewhere
        # therefore we load everything into this dictionary upfront
        tasks = []
        for op in operations:
            tasks.append(
                {
                    'db_object': op,
                    'id': op.id,
                    'operation': op.operation,
                    'scheduled_on': op.scheduled_on,
                    'property_changes': op.property_changes,
                    'content': self.repository.getContent(op._content.uniqueid),
                }
            )

        for task in tasks:
            try:
                self._execute_operations(task)
            except Exception as e:
                log.warning('Skip operation %s due to %s', task['id'], e)
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(e)

        for _ in commit_with_retry():
            pass

    def _execute_operations(self, task):
        content = task['content']
        if not content:
            log.warning('Content not found for operation %s, deleting operation', task['id'])
            self.session.delete(task['db_object'])
            return

        self._apply_property_changes(content, task['property_changes'])
        if task['operation'] == 'publish':
            self._execute_publish(content)
        elif task['operation'] == 'retract':
            self._execute_retract(content)
        else:
            # the forbidden route that we will never hit, I promise
            log.warning('Unknown operation type: %s', task['operation'])

        self.session.delete(task['db_object'])

    def _apply_property_changes(self, content, property_changes):
        if not property_changes:
            return

        with zeit.cms.checkout.helper.checked_out(
            content, will_publish_soon=True, raise_if_error=True
        ) as co:
            for name, new_value in property_changes.items():
                if hasattr(co, name):
                    old_value = getattr(co, name, None)
                    setattr(co, name, new_value)
                    self.objectlog.log(
                        content,
                        msg(
                            '${name} changed from "${old}" to "${new}"',
                            mapping={'name': name, 'old': old_value, 'new': new_value},
                        ),
                    )
                else:
                    log.warning('Property %s not found on %s', name, content.uniqueId)

    def _execute_publish(self, content):
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        publish.publish(background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED)

    def _execute_retract(self, content):
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if not info.published:
            log.info('Content %s already retracted, skipping', content.uniqueId)
            return

        publish = zeit.cms.workflow.interfaces.IPublish(content)
        publish.retract(background=False, priority=zeit.cms.workflow.interfaces.PRIORITY_TIMEBASED)


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.workflow', 'schedule-principal'))
def execute_scheduled_operations_cli():
    executor = ScheduledOperationProcessor()
    executor.execute_all()
