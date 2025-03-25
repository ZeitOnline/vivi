import logging

import zope.component
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
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
