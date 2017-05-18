from zeit.cms.content.interfaces import WRITEABLE_LIVE, WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import datetime
import lovely.remotetask.interfaces
import pytz
import rwproperty
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publishinfo
import zope.component
import zope.interface


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS


class TimeBasedWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Timebased workflow."""

    zope.interface.implements(zeit.workflow.interfaces.ITimeBasedPublishing)

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[0],
        WORKFLOW_NS, 'released_from', writeable=WRITEABLE_ALWAYS)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[1],
        WORKFLOW_NS, 'released_to', writeable=WRITEABLE_ALWAYS)

    publish_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Int(), WORKFLOW_NS, 'publish_job_id',
        writeable=WRITEABLE_LIVE)
    retract_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Int(), WORKFLOW_NS, 'retract_job_id',
        writeable=WRITEABLE_LIVE)

    def __init__(self, context):
        self.context = self.__parent__ = context

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_to

    @rwproperty.setproperty
    def release_period(self, value):
        """When setting the release period jobs to publish retract are created.
        """
        if value is None:
            value = None, None
        released_from, released_to = value
        if self.released_from != released_from:
            self.setup_job('publish', released_from)
        if self.released_to != released_to:
            self.setup_job('retract', released_to)
        self.released_from, self.released_to = value

    def setup_job(self, taskname, timestamp):
        _msg = _  # Avoid i18nextract picking up constructed messageids.
        jobid = lambda: getattr(self, '%s_job_id' % taskname)  # noqa
        cancelled = self.cancel_job(jobid())
        if cancelled:
            self.log(_msg(
                'timebased-%s-cancel' % taskname,
                default='Scheduled %s cancelled (job #${job}).' % taskname,
                mapping={'job': jobid()}))
            setattr(self, '%s_job_id' % taskname, None)
        if timestamp is not None:
            setattr(self, '%s_job_id' % taskname, self.add_job(
                'zeit.workflow.%s' % taskname, timestamp))
            self.log(_msg(
                'timebased-%s-add' % taskname,
                default='To %s on ${date} (job #${job})' % taskname,
                mapping={
                    'date': self.format_datetime(timestamp), 'job': jobid()}))

    def add_job(self, task_name, when):
        delay = when - datetime.datetime.now(pytz.UTC)
        delay = 60 * 60 * 24 * delay.days + delay.seconds  # Ignore microsecond
        task_description = zeit.workflow.publish.SingleInput(self.context)
        if delay > 0:
            job_id = self.tasks.addCronJob(
                unicode(task_name), task_description, delay=delay)
        else:
            job_id = self.tasks.add(unicode(task_name), task_description)
        return job_id

    def cancel_job(self, job_id):
        if not job_id:
            return False
        try:
            status = self.tasks.getStatus(job_id)
        except KeyError:
            return False
        if status != lovely.remotetask.interfaces.DELAYED:
            return False
        self.tasks.cancel(job_id)
        return True

    @property
    def tasks(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        queue = config['task-queue-%s' % PRIORITY_DEFAULT]
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)

    def log(self, message):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(self.context, message)

    @staticmethod
    def format_datetime(dt):
        interaction = zope.security.management.getInteraction()
        request = interaction.participations[0]
        tzinfo = zope.interface.common.idatetime.ITZInfo(request, None)
        if tzinfo is not None:
            dt = dt.astimezone(tzinfo)
        formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        return formatter.format(dt)


# Declare the messageids we dynamically construct in setup_job(), so
# i18nextract can find them.
_('timebased-publish-add')
_('timebased-publish-cancel')
_('timebased-retract-add')
_('timebased-retract-cancel')


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the expire/publication time to feed entry."""

    target_iface = zeit.workflow.interfaces.ITimeBasedPublishing

    def update_with_context(self, entry, workflow):
        date = ''
        if workflow.released_from:
            date = workflow.released_from.isoformat()
        entry.set('publication-date', date)

        date = ''
        if workflow.released_to:
            date = workflow.released_to.isoformat()
        entry.set('expires', date)
