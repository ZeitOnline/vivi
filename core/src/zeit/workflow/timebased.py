import logging

import zope.component
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.celery
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publishinfo
import zeit.workflow.scheduled.interfaces


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS

log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.workflow.interfaces.ITimeBasedPublishing)
class TimeBasedWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Timebased workflow."""

    _released_from = zeit.cms.content.dav.DAVProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing['release_period'].fields[0],
        WORKFLOW_NS,
        'released_from',
        writeable=WRITEABLE_ALWAYS,
    )
    _released_to = zeit.cms.content.dav.DAVProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing['release_period'].fields[1],
        WORKFLOW_NS,
        'released_to',
        writeable=WRITEABLE_ALWAYS,
    )

    def __init__(self, context):
        self.context = self.__parent__ = context

    @property
    def released_from(self):
        if FEATURE_TOGGLES.find('use_scheduled_operations'):
            try:
                ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
                if publish_ops := ops.list(operation='publish'):
                    return publish_ops[0].scheduled_on
            except Exception as e:
                log.warning('Error reading scheduled operations, falling back: %s', e)
        return self._released_from

    @released_from.setter
    def released_from(self, value):
        if FEATURE_TOGGLES.find('use_scheduled_operations'):
            try:
                ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
                existing = ops.list(operation='publish')

                if value is None:
                    for op in existing:
                        ops.remove(op.id)
                elif existing:
                    ops.update(existing[0].id, scheduled_on=value)
                else:
                    ops.add('publish', value)
            except Exception as e:
                log.warning('Error updating scheduled operations, falling back: %s', e)
                self._released_from = value
        else:
            self._released_from = value

    @property
    def released_to(self):
        if FEATURE_TOGGLES.find('use_scheduled_operations'):
            try:
                ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
                if retract_ops := ops.list(operation='retract'):
                    return retract_ops[0].scheduled_on
            except Exception as e:
                log.warning('Error reading scheduled operations, falling back: %s', e)
        return self._released_to

    @released_to.setter
    def released_to(self, value):
        if FEATURE_TOGGLES.find('use_scheduled_operations'):
            try:
                ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
                existing = ops.list(operation='retract')

                if value is None:
                    for op in existing:
                        ops.remove(op.id)
                elif existing:
                    ops.update(existing[0].id, scheduled_on=value)
                else:
                    ops.add('retract', value)
            except Exception as e:
                log.warning('Error updating scheduled operations, falling back: %s', e)
                self._released_to = value
        else:
            self._released_to = value

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
            self.log('publish', released_from)
        if self.released_to != released_to:
            self.log('retract', released_to)
        self.released_from = released_from
        self.released_to = released_to

    def log(self, task, timestamp):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        _msg = _  # Avoid i18nextract picking up constructed messageids.
        if timestamp is not None:
            log.log(
                self.context,
                _msg(
                    'timebased-%s-add' % task,
                    default='To %s on ${date}' % task,
                    mapping={'date': self.format_datetime(timestamp)},
                ),
            )

    @staticmethod
    def format_datetime(dt):
        interaction = zope.security.management.getInteraction()
        request = interaction.participations[0]
        tzinfo = zope.interface.common.idatetime.ITZInfo(request, None)
        if tzinfo is not None:
            dt = dt.astimezone(tzinfo)
        formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        return formatter.format(dt)


# Declare the messageids we dynamically construct in log(), so
# i18nextract can find them.
_('timebased-publish-add')
_('timebased-retract-add')
