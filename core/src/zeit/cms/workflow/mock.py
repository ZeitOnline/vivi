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

    def can_publish(self):
        return _can_publish.get(self.context.uniqueId, False)

    def publish(self):
        if not self.can_publish():
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Cannot publish.")
        print "Publishing: %s" % self.context.uniqueId

    def unpublish(self):
        raise NotImplementedError


    # Test support

    def set_can_publish(self, can):
        _can_publish[self.context.uniqueId] = can
