import argparse

from sqlalchemy import select
from sqlalchemy import text as sql
import opentelemetry.trace
import zope.component

from zeit.cms.cli import commit_with_retry, runner
from zeit.connector.models import Content as ConnectorModel
import zeit.cms.workflow.interfaces


def delete_temporary_imagegroups(query_min_age, query_max_age):
    query_timeout = int(zeit.cms.config.get('zeit.content.image', 'query-timeouts-ms', 10000))
    sql_query = """
        name like '%.tmp' and
        type = 'image-group' and
        last_updated < NOW() - INTERVAL ':min_age hour' and
        last_updated > NOW() - INTERVAL ':max_age days'
    """
    query = select(ConnectorModel)
    query = query.where(
        sql(sql_query).bindparams(min_age=int(query_min_age), max_age=int(query_max_age))
    )
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    for content in list(repository.search(query, query_timeout)):
        for _ in commit_with_retry():
            try:
                folder = content.__parent__
                del folder[content.__name__]
            except Exception as e:
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(e)


@runner()
def delete_temporary_images():
    query_max_age = int(zeit.cms.config.get('zeit.content.image', 'query-days-age-max', 1))
    query_min_age = int(zeit.cms.config.get('zeit.content.image', 'query-hours-age-min', 1))

    parser = argparse.ArgumentParser(description='Deletes temporary images')
    parser.add_argument('--min-age', help='Minimum age in hours', default=query_min_age)
    parser.add_argument('--max-age', help='Maximum age in days', default=query_max_age)
    options = parser.parse_args()
    delete_temporary_imagegroups(options.query_min_age, options.query_max_age)
