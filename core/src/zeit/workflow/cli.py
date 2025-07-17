import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import opentelemetry.trace
import zope.component

from zeit.cms.cli import commit_with_retry, from_config, runner
from zeit.connector.models import Content as ConnectorModel
import zeit.cms.workflow.interfaces


log = logging.getLogger(__name__)


def _handle_scheduled_content(action, sql_query, **params):
    query_timeout = int(zeit.cms.config.get('zeit.workflow', 'scheduled-query-timeouts-ms', 10000))
    bind_params = {key: value for key, value in params.items()}
    query = select(ConnectorModel)
    query = query.where(sql(sql_query).bindparams(**bind_params))
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    for content in repository.search(query, query_timeout):
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        for _ in commit_with_retry():
            try:
                func = getattr(publish, action)
                func(background=False)
            except Exception as e:
                log.warning('Skip %s due to %s', content, e)
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(e)


def _retract_scheduled_content():
    """Only retract content that has been published before scheduled retract"""
    retract_restrict_days = int(
        zeit.cms.config.get('zeit.workflow', 'scheduled-query-retract-restrict-days', 30)
    )
    sql_query = """
        published = true
        AND date_scheduled_retract >= CURRENT_DATE - INTERVAL ':restrict days'
        AND date_last_published <= date_scheduled_retract
        AND date_scheduled_retract <= NOW()
    """
    _handle_scheduled_content('retract', sql_query, restrict=retract_restrict_days)


def _publish_scheduled_content():
    """We must ensure that the scheduled retract is not too close"""
    publish_retract_margin = int(
        zeit.cms.config.get('zeit.workflow', 'scheduled-query-publish-margin-minutes', 10)
    )
    publish_restrict_days = int(
        zeit.cms.config.get('zeit.workflow', 'scheduled-query-publish-restrict-days', 30)
    )
    sql_query = """
        (published=False or date_last_published < date_scheduled_publish)
        AND date_scheduled_publish <= NOW()
        AND date_scheduled_publish >= CURRENT_DATE - INTERVAL ':restrict days'
        AND (date_last_retracted IS NULL OR date_last_retracted < date_scheduled_publish)
        AND (
          date_scheduled_retract IS NULL
          OR date_scheduled_retract > date_scheduled_publish + INTERVAL ':margin minutes'
        )
    """
    _handle_scheduled_content(
        'publish', sql_query, margin=publish_retract_margin, restrict=publish_restrict_days
    )


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def retract_scheduled_content():
    _retract_scheduled_content()


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def publish_scheduled_content():
    _publish_scheduled_content()
