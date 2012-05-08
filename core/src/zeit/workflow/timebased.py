# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
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


class TimeBasedWorkflow(zeit.workflow.publishinfo.NotPublishablePublishInfo):
    """Timebased workflow."""

    zope.interface.implements(zeit.workflow.interfaces.ITimeBasedPublishing)

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[0],
        WORKFLOW_NS, 'released_from', writeable=WRITEABLE_LIVE)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[1],
        WORKFLOW_NS, 'released_to', writeable=WRITEABLE_LIVE)

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
            cancelled = self.cancel_job(self.publish_job_id)
            if cancelled:
                self.log(
                    _('scheduled-publishing-cancelled',
                      default=(u"Scheduled publication cancelled "
                               "(job #${job})."),
                      mapping=dict(job=self.publish_job_id)))
            if released_from is not None:
                self.publish_job_id = self.add_job(
                    u'zeit.workflow.publish',
                    released_from)
                self.log(_('scheduled-for-publishing-on',
                           default=u"To be published on ${date} (job #${job})",
                           mapping=dict(
                               date=self.format_datetime(released_from),
                               job=self.publish_job_id)))

        if self.released_to != released_to:
            cancelled = self.cancel_job(self.retract_job_id)
            if cancelled:
                self.log(
                    _('scheduled-retracting-cancelled',
                      default=(u"Scheduled retracting cancelled "
                               "(job #${job})."),
                      mapping=dict(job=self.publish_job_id)))
            if released_to is not None:
                self.retract_job_id = self.add_job(
                    u'zeit.workflow.retract',
                    released_to)
                self.log(_('scheduled-for-retracting-on',
                           default=u"To be retracted on ${date} (job #${job})",
                           mapping=dict(
                               date=self.format_datetime(released_to),
                               job=self.retract_job_id)))

        self.released_from, self.released_to = value

    def add_job(self, task_name, when):
        delay = when - datetime.datetime.now(pytz.UTC)
        delay = 60*60*24 * delay.days + delay.seconds  # Ignore microseconds
        task_description = zeit.workflow.publish.TaskDescription(self.context)
        if delay > 0:
            job_id = self.tasks.addCronJob(
                task_name, task_description, delay=delay)
        else:
            job_id = self.tasks.add(task_name, task_description)
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
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')

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
