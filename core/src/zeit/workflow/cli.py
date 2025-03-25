import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import z3c.celery.celery
import zope.component

from zeit.cms.cli import commit_with_retry, from_config, runner
from zeit.connector.models import Content as ConnectorModel
import zeit.cms.workflow.interfaces


log = logging.getLogger(__name__)


def _handle_scheduled_content(action, sql_query):
    query = select(ConnectorModel)
    query = query.where(sql(sql_query))
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
                    break
                raise


def _retract_scheduled_content():
    sql_query = """
        published = true
        AND date_scheduled_retract <= NOW()
    """
    _handle_scheduled_content('retract', sql_query)


def _publish_scheduled_content():
    sql_query = """
        published = false
        AND date_scheduled_publish <= NOW()
    """
    _handle_scheduled_content('publish', sql_query)


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def retract_scheduled_content():
    _retract_scheduled_content()


@runner(principal=from_config('zeit.workflow', 'schedule-principal'))
def publish_scheduled_content():
    _publish_scheduled_content()
