import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload
import opentelemetry.trace
import pendulum
import zope.component

from zeit.cms.cli import commit_with_retry
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.connector.models import ScheduledOperation
from zeit.workflow.scheduled.interfaces import IScheduledOperation, IScheduledOperations
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.repository.interfaces
import zeit.connector.interfaces


log = logging.getLogger(__name__)


def execute_scheduled_operations():
    query_timeout = int(zeit.cms.config.get('zeit.workflow', 'scheduled-query-timeouts-ms', 10000))
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    query = (
        select(ScheduledOperation)
        .where(
            ScheduledOperation.scheduled_on <= pendulum.now('UTC'),
            ScheduledOperation.executed_on.is_(None),
        )
        .order_by(ScheduledOperation.scheduled_on)
        .options(joinedload(ScheduledOperation._content))
    )

    raw_operations = connector.execute_sql(query, query_timeout).scalars().all()
    log.debug('Found %d scheduled operations to execute', len(raw_operations))

    # Extract data from SQL models before they become detached from session
    operations = [(IScheduledOperation(op), op._content.uniqueid) for op in raw_operations]

    for operation, content_uniqueid in operations:
        for _ in commit_with_retry():
            try:
                content = repository.getContent(content_uniqueid)
                if not content:
                    log.warning('Content not found for operation %s, skipping', operation.id)
                    continue

                ops = IScheduledOperations(content)
                ops.execute(operation)
            except Exception as e:
                log.warning('Skip operation %s due to %s', operation.id, e)
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(e)


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.workflow', 'schedule-principal'))
def execute_scheduled_operations_cli():
    if not FEATURE_TOGGLES.find('use_scheduled_cronjob'):
        return
    execute_scheduled_operations()
