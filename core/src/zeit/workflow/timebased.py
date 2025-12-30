import logging

import pendulum
import zope.component
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.celery
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.content.interfaces
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
            self.log('publish', released_from)
        if self.released_to != released_to:
            self.log('retract', released_to)
        self.released_from, self.released_to = value

        self._sync_scheduled_operations(released_from, released_to)

    def log(self, task, timestamp):
        if FEATURE_TOGGLES.find('use_scheduled_operations'):
            return
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

    def _sync_scheduled_operations(self, released_from, released_to):
        if not FEATURE_TOGGLES.find('use_scheduled_operations'):
            return

        try:
            uuid = zeit.cms.content.interfaces.IUUID(self.context).shortened
        except (TypeError, AttributeError):
            log.debug(
                'Skipping scheduled operations sync (no UUID yet): %s',
                getattr(self.context, 'uniqueId', '<unknown>'),
            )
            return

        if not uuid:
            log.debug(
                'Skipping scheduled operations sync (empty UUID): %s',
                getattr(self.context, 'uniqueId', '<unknown>'),
            )
            return

        try:
            ops = zeit.workflow.scheduled.interfaces.IScheduledOperations(self.context)
        except zope.component.ComponentLookupError:
            log.debug('IScheduledOperations adapter not available for %s', self.context.uniqueId)
            return

        self._create_or_update_operation(ops, 'publish', released_from)
        self._create_or_update_operation(ops, 'retract', released_to)

    def _create_or_update_operation(self, ops, operation, scheduled_on):
        # Only manage simple operations, don't touch channel/access scheduling
        existing = [op for op in ops.list(operation=operation) if not op.property_changes]
        scheduled_op = existing[0] if existing else None

        if scheduled_on and scheduled_on >= pendulum.now('UTC'):
            if scheduled_op:
                ops.update(scheduled_op.id, scheduled_on=scheduled_on)
            else:
                ops.add(operation, scheduled_on)
        elif scheduled_op:
            ops.remove(scheduled_op.id)


# Declare the messageids we dynamically construct in log(), so
# i18nextract can find them.
_('timebased-publish-add')
_('timebased-retract-add')
