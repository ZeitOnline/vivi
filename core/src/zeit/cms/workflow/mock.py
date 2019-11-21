from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
from zeit.cms.workflow.interfaces import PRIORITY_LOW
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


class MockPublish(object):
    """A mock publisher."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)

    def __init__(self, context):
        self.context = context

    def publish(self, priority=PRIORITY_DEFAULT, async=True,
                object=None, **kw):
        if object:
            self.context = object
        can_publish = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).can_publish()
        if can_publish != CAN_PUBLISH_SUCCESS:
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Cannot publish.")
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(self.context,
                                                            self.context))
        print("Publishing: %s" % self.context.uniqueId)
        _published[self.context.uniqueId] = True
        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(self.context,
                                                        self.context))

    def retract(
            self, priority=PRIORITY_DEFAULT, async=True, object=None, **kw):
        if object:
            self.context = object
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(self.context,
                                                            self.context))
        print("Retracting: %s" % self.context.uniqueId)
        _published[self.context.uniqueId] = False
        zope.event.notify(
            zeit.cms.workflow.interfaces.RetractedEvent(self.context,
                                                        self.context))

    def publish_multiple(
            self, objects, priority=PRIORITY_LOW, async=True, **kw):
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.publish(priority, async, obj)

    def retract_multiple(
            self, objects, priority=PRIORITY_LOW, async=True, **kw):
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.retract(priority, async, obj)


class MockPublishInfo(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    error_messages = ()
    date_print_published = None
    last_modified_by = u'testuser'
    last_published_by = u'testuser'
    locked = False
    lock_reason = None

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

    @property
    def date_first_released(self):
        return _publish_times_first.get(self.context.uniqueId)

    @date_first_released.setter
    def date_first_released(self, value):
        _publish_times_first[self.context.uniqueId] = value

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
_publish_times_first = {}


def reset():
    _can_publish.clear()
    _published.clear()
    _publish_times.clear()
    _publish_times_semantic.clear()
    _publish_times_first.clear()

try:
    import zope.testing.cleanup
    zope.testing.cleanup.addCleanUp(reset)
except ImportError:
    pass
