import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import opentelemetry.trace
import z3c.celery.celery
import zope.component

from zeit.cms.cli import commit_with_retry, from_config, runner
from zeit.connector.models import Content as ConnectorModel
import zeit.cms.workflow.interfaces


log = logging.getLogger(__name__)


def _handle_scheduled_content(action, sql_query, **params):
    bind_params = {key: value for key, value in params.items()}
    bind_params['age'] = int(
        zeit.cms.config.get('zeit.workflow', 'scheduled-query-restrict-days', 60)
    )
    sql_query += """ AND last_updated >= CURRENT_DATE - INTERVAL ':age days'"""
    query = select(ConnectorModel)
    query = query.where(sql(sql_query).bindparams(**bind_params))
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    results = repository.search(query)
    for content in results:
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        for _ in commit_with_retry():
            try:
                func = getattr(publish, action)
                func(background=False)
            except z3c.celery.celery.HandleAfterAbort as e:
                if 'LockingError' in e.message:  # kludgy
                    log.warning('Skip %s due to %s', content, e.message)
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(e)


def _retract_scheduled_content():
    """Only retract content that has been published before scheduled retract"""
    sql_query = """
        published = true
        AND date_last_published <= date_scheduled_retract
        AND date_scheduled_retract <= NOW()
    """
    _handle_scheduled_content('retract', sql_query)


def _publish_scheduled_content():
    """We must ensure that we do not republish manually retracted content.
    Therefore check that the scheduled publish date is not older than n-minutes.
    """
    restrict_publish_days = int(
        zeit.cms.config.get('zeit.workflow', 'scheduled-publish-query-restrict-minutes', 60)
    )
    sql_query = """
        published = false
        AND date_scheduled_publish <= NOW()
        AND date_last_retracted <= date_scheduled_publish
        AND date_scheduled_publish > NOW() - INTERVAL ':publish minutes'
    """
    _handle_scheduled_content('publish', sql_query, publish=restrict_publish_days)


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def retract_scheduled_content():
    _retract_scheduled_content()


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def publish_scheduled_content():
    _publish_scheduled_content()
