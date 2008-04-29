# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""A mock workflow component for testing."""

import zope.component
import zope.interface
import zope.testing.cleanup

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


_can_publish = {}
zope.testing.cleanup.addCleanUp(_can_publish.clear)


class MockPublish(object):
    """A mock publisher."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)

    def __init__(self, context):
        self.context = context

    def publish(self):
        if not zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).can_publish():
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Cannot publish.")
        print "Publishing: %s" % self.context.uniqueId

    def retract(self):
        raise NotImplementedError


_published = {}
zope.testing.cleanup.addCleanUp(_published.clear)
_publish_times = {}
zope.testing.cleanup.addCleanUp(_publish_times.clear)


class MockPublishInfo(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    date_first_released = None
    last_modified_by = u'testuser'

    def __init__(self, context):
        self.context = context

    @property
    def published(self):
        return _published.get(self.context.uniqueId, False)

    @property
    def date_last_published(self):
        return _publish_times.get(self.context.uniqueId)

    def can_publish(self):
        return _can_publish.get(self.context.uniqueId, False)

    # Test support

    def set_can_publish(self, can):
        _can_publish[self.context.uniqueId] = can
