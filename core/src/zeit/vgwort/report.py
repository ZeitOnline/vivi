from __future__ import print_function
from zeit.cms.content.interfaces import WRITEABLE_LIVE
import ZODB.POSException
import datetime
import gocept.runner
import grokcore.component
import logging
import os.path
import pytz
import sys
import tempfile
import zc.lockfile
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


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
            (sv.FIRST_RELEASED < age) & (sv.PRIVATE_TOKEN > '') &
            (sv.REPORTED_ON == '') & (sv.REPORTED_ERROR == ''))
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
    lock_file_name = os.path.join(tempfile.gettempdir(), 'vgwort-run-lock')
    try:
        lock = zc.lockfile.LockFile(lock_file_name)
    except zc.lockfile.LockError:
        print("VGWort report alredy running? Could not lock {}".format(
              lock_file_name), file=sys.stderr)
        sys.exit(1)

    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    four = today.replace(hour=3, minute=50)
    six = today.replace(hour=6, minute=10)
    if four <= now <= six:
        print('VGWort API maintenance window between 04:00-06:00, exiting',
              file=sys.stderr)
        sys.exit(2)

    try:
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        for content in source:
            try:
                report(content)
            except Exception:
                log.warning(
                    'Error reporting %s, ignoring', content, exc_info=True)
    finally:
        lock.close()


def report(context):
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
