from zeit.cms.content.interfaces import WRITEABLE_LIVE
import ZODB.POSException
import datetime
import grokcore.component as grok
import logging
import os.path
import pytz
import six
import sys
import tempfile
import zc.lockfile
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.find.interfaces
import zeit.retresco.update
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.vgwort.interfaces.IReportableContentSource)
class ReportableContentSource(grok.GlobalUtility):

    def __iter__(self):
        age = self.config['days-before-report']
        age = datetime.date.today() - datetime.timedelta(days=int(age))
        age = age.isoformat()

        i = 0
        result = self._query(age, i)
        while len(result) < result.hits:
            i += 1
            result.extend(self._query(age, i))

        for row in result:
            content = zeit.cms.interfaces.ICMSContent(
                zeit.cms.interfaces.ID_NAMESPACE[:-1] + row['url'], None)
            if content is not None:
                yield content

    def _query(self, age, page=0, rows=100):
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        return elastic.search({'query': {'bool': {'filter': [
            {'exists': {'field': 'payload.vgwort.private_token'}},
            {'range': {'payload.document.date_first_released': {'lte': age}}},
        ], 'must_not': [
            {'exists': {'field': 'payload.vgwort.reported_on'}},
            {'exists': {'field': 'payload.vgwort.reported_error'}},
        ]}}, '_source': ['url']}, start=page * rows, rows=rows)

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

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')


class ReportInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.provides(zeit.vgwort.interfaces.IReportInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IReportInfo,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('reported_on', 'reported_error'),
        writeable=WRITEABLE_LIVE)


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config(
    'zeit.vgwort', 'token-principal'))
def report_new_documents():
    lock_file_name = os.path.join(tempfile.gettempdir(), 'vgwort-run-lock')
    try:
        lock = zc.lockfile.LockFile(lock_file_name)
    except zc.lockfile.LockError:
        sys.stderr.write(
            "VGWort report alredy running? Could not lock {}\n".format(
                lock_file_name))
        sys.exit(1)

    log.info('Report start')
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    four = today.replace(hour=3, minute=50)
    six = today.replace(hour=6, minute=10)
    if four <= now <= six:
        sys.stderr.write(
            'VGWort API maintenance window between 04:00-06:00, exiting\n')
        sys.exit(2)

    vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
    try:
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        for i, content in enumerate(source):
            try:
                report(content)
            except Exception as e:
                try:
                    if e.args[0][0] == 401:
                        raise
                except IndexError:
                    pass
                log.warning(
                    'Error reporting %s, ignoring', content, exc_info=True)
            # XXX vgwort returns 401 after some requests for unknown reasons.
            if i % 6 == 0 and 'client' in vgwort.__dict__:
                del vgwort.client
    finally:
        lock.close()
    log.info('Report end')


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
    except zeit.vgwort.interfaces.TechnicalError:
        log.warning(
            'technical error reporting %s, will be retried on the next run'
            % context.uniqueId, exc_info=True)
    except zeit.vgwort.interfaces.WebServiceError as e:
        log.warning(
            'semantic error reporting %s' % context.uniqueId, exc_info=True)
        source.mark_error(context, six.text_type(e))
