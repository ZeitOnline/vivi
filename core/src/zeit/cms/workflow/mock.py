import celery.result
import celery.states
import zope.component
import zope.interface

from zeit.cms.workflow.interfaces import (
    CAN_PUBLISH_ERROR,
    CAN_RETRACT_ERROR,
    PRIORITY_DEFAULT,
    PRIORITY_LOW,
)
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublish)
class MockPublish:
    """A mock publisher."""

    def __init__(self, context):
        self.context = context

    def _result(self):
        return celery.result.EagerResult('eager', None, celery.states.SUCCESS)

    def publish(self, priority=PRIORITY_DEFAULT, background=True, object=None, **kw):
        if object is not None:
            self.context = object
        self.context = zope.security.proxy.getObject(self.context)
        can_publish = zeit.cms.workflow.interfaces.IPublishInfo(self.context).can_publish()
        if can_publish == CAN_PUBLISH_ERROR:
            raise zeit.cms.workflow.interfaces.PublishingError('Cannot publish.')
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        info.published = True
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(self.context, self.context)
        )
        print('Publishing: %s' % self.context.uniqueId)
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(self.context, self.context))
        return self._result()

    def retract(self, priority=PRIORITY_DEFAULT, background=True, object=None, **kw):
        if object is not None:
            self.context = object
        self.context = zope.security.proxy.getObject(self.context)
        can_retract = zeit.cms.workflow.interfaces.IPublishInfo(self.context).can_retract()
        if can_retract == CAN_RETRACT_ERROR:
            raise zeit.cms.workflow.interfaces.RetractError('Cannot retract.')
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(self.context, self.context)
        )
        print('Retracting: %s' % self.context.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        info.published = False
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(self.context, self.context))
        return self._result()

    def publish_multiple(self, objects, priority=PRIORITY_LOW, background=True, **kw):
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.publish(priority, background, obj)
        return self._result()

    def retract_multiple(self, objects, priority=PRIORITY_LOW, background=True, **kw):
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.retract(priority, background, obj)
        return self._result()


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
class MockPublishInfo:
    error_messages = ()
    date_print_published = None
    last_modified_by = 'testuser'
    last_published_by = 'testuser'
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
            self.context.uniqueId, zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        )

    def can_retract(self):
        return _can_retract.get(
            self.context.uniqueId, zeit.cms.workflow.interfaces.CAN_RETRACT_SUCCESS
        )

    # Test support

    def set_can_publish(self, can):
        _can_publish[self.context.uniqueId] = can

    def set_can_retract(self, can):
        _can_retract[self.context.uniqueId] = can


_can_publish = {}
_can_retract = {}
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


@zope.component.adapter(zeit.cms.workflow.interfaces.IPublishInfo)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflow_dav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)
