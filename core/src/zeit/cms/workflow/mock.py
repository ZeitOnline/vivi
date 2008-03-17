# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""A mock workflow component for testing."""

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


class MockPublish(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)

    def __init__(self, context):
        self.context = context

    def publish(self):
        print "Publishing: %s" % self.context.uniqueId
