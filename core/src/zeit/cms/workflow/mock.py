from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface
import zope.testing.cleanup


class MockPublish(object):
    """A mock publisher."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)

    def __init__(self, context):
        self.context = context

    def publish(self, priority=PRIORITY_DEFAULT, async=True):
        can_publish = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).can_publish()
        if can_publish != CAN_PUBLISH_SUCCESS:
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Cannot publish.")
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(self.context,
                                                            self.context))
        print "Publishing: %s" % self.context.uniqueId
        _published[self.context.uniqueId] = True
        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(self.context,
                                                        self.context))

    def retract(self, priority=PRIORITY_DEFAULT, async=True):
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(self.context,
                                                            self.context))
        print "Retracting: %s" % self.context.uniqueId
        _published[self.context.uniqueId] = False
        zope.event.notify(
            zeit.cms.workflow.interfaces.RetractedEvent(self.context,
                                                        self.context))


class MockPublishInfo(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    error_messages = ()
    date_first_released = None
    date_print_published = None
    last_modified_by = u'testuser'
    last_published_by = u'testuser'

    def __init__(self, context):
        self.context = context

    @property
    def published(self):
        return _published.get(self.context.uniqueId, False)

    @published.setter
    def published(self, value):
        _published[self.context.uniqueId] = value

    @property
    def date_last_published(self):
        return _publish_times.get(self.context.uniqueId)

    @date_last_published.setter
    def date_last_published(self, value):
        _publish_times[self.context.uniqueId] = value

    @property
    def date_last_published_semantic(self):
        return _publish_times_semantic.get(self.context.uniqueId)

    @date_last_published_semantic.setter
    def date_last_published_semantic(self, value):
        _publish_times_semantic[self.context.uniqueId] = value

    def can_publish(self):
        return _can_publish.get(
            self.context.uniqueId,
            zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR)

    # Test support

    def set_can_publish(self, can):
        _can_publish[self.context.uniqueId] = can


_can_publish = {}
_published = {}
_publish_times = {}
_publish_times_semantic = {}


def reset():
    _can_publish.clear()
    _published.clear()
    _publish_times.clear()
    _publish_times_semantic.clear()
zope.testing.cleanup.addCleanUp(reset)
