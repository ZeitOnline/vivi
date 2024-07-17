import datetime
import logging

import grokcore.component as grok
import pytz
import ZODB.POSException
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.vgwort.interfaces import in_daily_maintenance_window
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.find.interfaces
import zeit.retresco.update
import zeit.vgwort.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.vgwort.interfaces.IReportableContentSource)
class ReportableContentSource(grok.GlobalUtility):
    def __iter__(self):
        age = zeit.cms.config.required('zeit.vgwort', 'days-before-report')
        age = datetime.date.today() - datetime.timedelta(days=int(age))
        age = age.isoformat()

        i = 0
        result = self._query(age, i)
        while len(result) < result.hits:
            i += 1
            result.extend(self._query(age, i))

        for row in result:
            content = zeit.cms.interfaces.ICMSContent(
                zeit.cms.interfaces.ID_NAMESPACE[:-1] + row['url'], None
            )
            if content is not None:
                yield content

    def _query(self, age, page=0, rows=100):
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        return elastic.search(
            {
                'query': {
                    'bool': {
                        'filter': [
                            {'exists': {'field': 'payload.vgwort.private_token'}},
                            {'range': {'payload.document.date_first_released': {'lte': age}}},
                        ],
                        'must_not': [
                            {'exists': {'field': 'payload.vgwort.reported_on'}},
                            {'exists': {'field': 'payload.vgwort.reported_error'}},
                        ],
                    }
                },
                '_source': ['url'],
            },
            start=page * rows,
            rows=rows,
        )

    def mark_done(self, content):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = datetime.datetime.now(pytz.UTC)
        self._update_tms(content)

    def mark_error(self, content, message):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_error = message
        self._update_tms(content)

    def mark_todo(self, content):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = None
        info.reported_error = None
        self._update_tms(content)

    def _update_tms(self, content):
        errors = zeit.retresco.update.index(content)
        if errors:
            raise errors[0]


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
    log.info('Report start')
    if in_daily_maintenance_window():
        log.info('Skip inside daily VG-Wort API maintenance window')
        return

    vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
    source = zope.component.getUtility(zeit.vgwort.interfaces.IReportableContentSource)
    for i, content in enumerate(source):
        try:
            report(content)

            info = zeit.vgwort.interfaces.IReportInfo(content)
            data = {
                x: getattr(info, x)
                for x in zope.schema.getFieldNames(zope.vgwort.interfaces.IReportInfo)
            }
            for _ in zeit.cms.cli.commit_with_retry():
                for key, value in data.items():
                    setattr(info, key, value)
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
    log.info('Report end')


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
