# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""A mock workflow component for testing."""

from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface
import zope.testing.cleanup


_can_publish = {}
zope.testing.cleanup.addCleanUp(_can_publish.clear)


class MockPublish(object):
    """A mock publisher."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)

    def __init__(self, context):
        self.context = context

    def publish(self, priority=PRIORITY_DEFAULT):
        if not zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).can_publish():
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

    def retract(self, priority=PRIORITY_DEFAULT):
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(self.context,
                                                            self.context))
        print "Retracting: %s" % self.context.uniqueId
        _published[self.context.uniqueId] = False
        zope.event.notify(
            zeit.cms.workflow.interfaces.RetractedEvent(self.context,
                                                        self.context))


_published = {}
zope.testing.cleanup.addCleanUp(_published.clear)
_publish_times = {}
zope.testing.cleanup.addCleanUp(_publish_times.clear)
_publish_times_semantic = {}
zope.testing.cleanup.addCleanUp(_publish_times_semantic.clear)


class MockPublishInfo(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    date_first_released = None
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
        return _can_publish.get(self.context.uniqueId, False)

    # Test support

    def set_can_publish(self, can):
        _can_publish[self.context.uniqueId] = can
