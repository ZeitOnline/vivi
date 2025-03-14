import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import grokcore.component as grok
import pendulum
import ZODB.POSException
import zope.component
import zope.event
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.connector.models import Content as ConnectorModel
from zeit.vgwort.interfaces import in_daily_maintenance_window
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.contentquery.interfaces
import zeit.find.interfaces
import zeit.retresco.update
import zeit.vgwort.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.vgwort.interfaces.IReportableContentSource)
class ReportableContentSource(grok.GlobalUtility):
    def __iter__(self):
        age = zeit.cms.config.required('zeit.vgwort', 'days-before-report')
        # larger timeframe -> risk of statement timeouts!
        age_limit = zeit.cms.config.required('zeit.vgwort', 'days-age-limit-report')
        query_timeout = zeit.cms.config.required('zeit.vgwort', 'query-timeout')

        sql_query = (
            "type = 'article'"
            ' AND date_first_released <= CURRENT_DATE - INTERVAL :age'
            ' AND date_first_released >= CURRENT_DATE - INTERVAL :age_limit'
            ' AND vgwort_private_token IS NOT NULL'
            ' AND vgwort_reported_on IS NULL'
            " AND vgwort_reported_error = ''"
        )

        query = select(ConnectorModel)
        query = query.where(
            sql(sql_query).bindparams(age=f'{age} days', age_limit=f'{age_limit} days')
        )

        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        results = repository.search(query, query_timeout)
        for resource in results:
            yield resource

    def mark_done(self, content):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = pendulum.now('UTC')

    def mark_error(self, content, message):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_error = message

    def mark_todo(self, content):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = None
        info.reported_error = None


class ReportInfo(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.provides(zeit.vgwort.interfaces.IReportInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IReportInfo,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('reported_on', 'reported_error'),
        writeable=WRITEABLE_LIVE,
    )


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.vgwort', 'token-principal'))
def report_new_documents():
    if in_daily_maintenance_window():
        log.info('Skip inside daily VG-Wort API maintenance window')
        return

    vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
    source = zope.component.getUtility(zeit.vgwort.interfaces.IReportableContentSource)
    for i, content in enumerate(source):
        try:
            for _ in zeit.cms.cli.commit_with_retry():
                report(content)
        except Exception as e:
            try:
                if e.args[0][0] == 401:
                    raise
            except IndexError:
                pass
            log.warning('Error reporting %s, ignoring', content, exc_info=True)
        # XXX vgwort returns 401 after some requests for unknown reasons.
        if i % 6 == 0 and 'client' in vgwort.__dict__:
            del vgwort.client


def report(context):
    source = zope.component.getUtility(zeit.vgwort.interfaces.IReportableContentSource)
    vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
    log.info('reporting %s' % context.uniqueId)
    try:
        vgwort.new_document(context)
        source.mark_done(context)
    except ZODB.POSException.ConflictError:
        raise
    except zeit.vgwort.interfaces.TechnicalError:
        log.warning(
            'technical error reporting %s, will be retried on the next run' % context.uniqueId,
            exc_info=True,
        )
    except zeit.vgwort.interfaces.WebServiceError as e:
        log.warning('semantic error reporting %s' % context.uniqueId, exc_info=True)
        source.mark_error(context, str(e))
