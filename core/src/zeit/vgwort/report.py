# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.POSException
import datetime
import gocept.async
import gocept.runner
import grokcore.component
import logging
import pytz
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.search
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


def SearchVar(name, ns):
    prefix = 'http://namespaces.zeit.de/CMS/'
    return zeit.connector.search.SearchVar(name, prefix + ns)


PUBLISHED = SearchVar('published', 'workflow')
FIRST_RELEASED = SearchVar('date_first_released', 'document')
AUTHOR = SearchVar('author', 'document')
PRIVATE_TOKEN = SearchVar('private_token', 'vgwort')
REPORTED_ON = SearchVar('reported_on', 'vgwort')
REPORTED_ERROR = SearchVar('reported_error', 'vgwort')


class ReportableContentSource(grokcore.component.GlobalUtility):

    zope.interface.implements(zeit.vgwort.interfaces.IReportableContentSource)

    def __iter__(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        age = self.config['days-before-report']
        last_week = datetime.date.today() - datetime.timedelta(days=int(age))
        last_week = last_week.isoformat()
        result = connector.search(
            [PUBLISHED],
            (PUBLISHED == 'yes') & (FIRST_RELEASED < last_week)
            & (PRIVATE_TOKEN > '') & (AUTHOR > '')
            & (REPORTED_ON == '') & (REPORTED_ERROR == ''))
        result = [zeit.cms.interfaces.ICMSContent(x[0]) for x in result]
        return iter(result)

    def mark_done(self, content):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = datetime.datetime.now(pytz.UTC)

    def mark_error(self, content, message):
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_error = message

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')


class ReportInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.provides(zeit.vgwort.interfaces.IReportInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IReportInfo,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('reported_on', 'reported_error'),
        live=True)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.vgwort', 'token-principal'))
def report_new_documents():
    source = zope.component.getUtility(
        zeit.vgwort.interfaces.IReportableContentSource)
    for content in source:
        async_report(content)


@gocept.async.function(u'events')
def async_report(context):
    report(context)


def report(context):
    log = logging.getLogger(__name__)
    source = zope.component.getUtility(
        zeit.vgwort.interfaces.IReportableContentSource)
    vgwort = zope.component.getUtility(
        zeit.vgwort.interfaces.IMessageService)
    log.info('reporting %s' % context.uniqueId)
    try:
        vgwort.new_document(context)
        source.mark_done(context)
    except ZODB.POSException.ConflictError:
        raise
    except zeit.vgwort.interfaces.TechnicalError, e:
        log.warning(
            'technical error reporting %s, will be retried on the next run'
            % context.uniqueId, exc_info=True)
    except zeit.vgwort.interfaces.WebServiceError, e:
        log.warning(
            'semantic error reporting %s' % context.uniqueId, exc_info=True)
        source.mark_error(context, str(e))
