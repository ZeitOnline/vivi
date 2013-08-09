# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_LIVE
import ZODB.POSException
import datetime
import gocept.async
import gocept.runner
import grokcore.component
import logging
import pytz
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


class ReportableContentSource(grokcore.component.GlobalUtility):

    zope.interface.implements(zeit.vgwort.interfaces.IReportableContentSource)

    def __iter__(self):
        result = self.query()
        return (zeit.cms.interfaces.ICMSContent(x[0]) for x in result)

    def query(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        age = self.config['days-before-report']
        age = datetime.date.today() - datetime.timedelta(days=int(age))
        age = age.isoformat()
        sv = zeit.vgwort.interfaces.SearchVars
        result = connector.search(
            [sv.FIRST_RELEASED, sv.PRIVATE_TOKEN,
             sv.REPORTED_ON, sv.REPORTED_ERROR],
            (sv.FIRST_RELEASED < age) & (sv.PRIVATE_TOKEN > '')
            & (sv.REPORTED_ON == '') & (sv.REPORTED_ERROR == ''))
        return result

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
        writeable=WRITEABLE_LIVE)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.vgwort', 'token-principal'))
def report_new_documents():
    source = zope.component.getUtility(
        zeit.vgwort.interfaces.IReportableContentSource)
    for content in source:
        report(content)


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
        source.mark_error(context, unicode(e))
