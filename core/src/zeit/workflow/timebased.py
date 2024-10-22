import logging

import grokcore.component as grok
import pendulum
import z3c.celery.celery
import zope.component
import zope.interface

from zeit.cms.cli import commit_with_retry
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import PRIORITY_TIMEBASED
import zeit.cms.celery
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publishinfo


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS

log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.workflow.interfaces.ITimeBasedPublishing)
class TimeBasedWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Timebased workflow."""

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing['release_period'].fields[0],
        WORKFLOW_NS,
        'released_from',
        writeable=WRITEABLE_ALWAYS,
    )
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing['release_period'].fields[1],
        WORKFLOW_NS,
        'released_to',
        writeable=WRITEABLE_ALWAYS,
    )

    publish_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Text(), WORKFLOW_NS, 'publish_job_id', writeable=WRITEABLE_ALWAYS
    )
    retract_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Text(), WORKFLOW_NS, 'retract_job_id', writeable=WRITEABLE_ALWAYS
    )

    def __init__(self, context):
        self.context = self.__parent__ = context

    @property
    def release_period(self):
        return self.released_from, self.released_to

    @release_period.setter
    def release_period(self, value):
        """When setting the release period jobs to publish retract are created."""
        if value is None:
            value = None, None
        released_from, released_to = value
        if self.released_from != released_from:
            self.setup_job('publish', released_from)
        if self.released_to != released_to:
            self.setup_job('retract', released_to)
        self.released_from, self.released_to = value

    def setup_job(self, task, timestamp):
        _msg = _  # Avoid i18nextract picking up constructed messageids.
        jobid = lambda: getattr(self, '%s_job_id' % task)  # NOQA
        cancelled = self.cancel_job(jobid())
        if cancelled:
            self.log(
                _msg(
                    'timebased-%s-cancel' % task,
                    default='Scheduled %s cancelled (job #${job}).' % task,
                    mapping={'job': jobid()},
                )
            )
            setattr(self, '%s_job_id' % task, None)
        if timestamp is not None:
            setattr(
                self,
                '%s_job_id' % task,
                self.add_job(getattr(zeit.workflow.publish, '%s_TASK' % task.upper()), timestamp),
            )
            self.log(
                _msg(
                    'timebased-%s-add' % task,
                    default='To %s on ${date} (job #${job})' % task,
                    mapping={'date': self.format_datetime(timestamp), 'job': jobid()},
                )
            )

    def add_job(self, task, when):
        # Special cases that keep piling up, sigh.
        renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(self.context)
        if renameable.renameable and renameable.rename_to:
            parent = zeit.cms.interfaces.ICMSContent(self.context.uniqueId).__parent__
            uniqueId = parent.uniqueId + renameable.rename_to
        else:
            uniqueId = self.context.uniqueId

        if when > pendulum.now('UTC'):
            job_id = task.apply_async(([uniqueId],), eta=when, queue=PRIORITY_TIMEBASED).id
        else:
            job_id = task.delay([uniqueId]).id
        return job_id

    def cancel_job(self, job_id):
        import celery_longterm_scheduler  # UI-only dependency

        if not job_id:
            return False
        return celery_longterm_scheduler.get_scheduler(zeit.cms.celery.CELERY).revoke(job_id)

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


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent)
def schedule_imported_retract_jobs(context, event):
    """Since the print-import (exporter.zeit.de) works only on the DAV-level,
    it can not create vivi jobs. Thus we do that here. (This especially applies
    to imagegroups.)
    """
    workflow = zeit.workflow.interfaces.ITimeBasedPublishing(context, None)
    if (
        workflow is None
        or workflow.retract_job_id
        or not workflow.released_to
        or workflow.released_to < pendulum.now('UTC')
    ):
        return
    workflow.setup_job('retract', workflow.released_to)


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.workflow', 'retract-timebased-principal')
)
def retract_overdue_objects():
    import zeit.find.interfaces
    import zeit.retresco.interfaces

    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    es = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
    unretracted = es.search(
        {
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'payload.workflow.published': True}},
                        {'range': {'payload.workflow.released_to': {'lt': 'now-15m'}}},
                    ]
                }
            },
            '_source': ['url', 'doc_id'],
        },
        rows=1000,
    )

    for item in unretracted:
        uniqueId = 'http://xml.zeit.de' + item['url']
        content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
        if content is None:
            log.info('Not found: %s, deleting from TMS', uniqueId)
            tms.delete_id(item['doc_id'])
        else:
            publish = zeit.cms.workflow.interfaces.IPublish(content)
            for _ in commit_with_retry():
                log.info('Retracting %s', content)
                try:
                    publish.retract(background=False)
                except z3c.celery.celery.HandleAfterAbort as e:
                    if 'LockingError' in e.message:  # kludgy
                        log.warning('Skip %s due to %s', content, e.message)
                        break
                    raise
