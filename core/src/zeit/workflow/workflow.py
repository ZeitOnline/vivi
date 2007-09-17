# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import rwproperty

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.dav

import zeit.workflow.interfaces


class LiveProperties(dict):
    """Webdav properties which are updated upon change."""

    def __init__(self, resource):
        super(LiveProperties, self).__init__(resource.properties)
        self.resource_id = resource.id

    def __setitem__(self, key, value):
        super(LiveProperties, self).__setitem__(key, value)
        self.connector.changeProperties(self.resource_id, {key: value})

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)



class Workflow(object):
    """Adapt ICMSContent to IWorkflow using the "live" data from connector.

    We must read and write properties directly from the DAV to be sure we
    actually can do the transition.
    """

    zope.interface.implements(zeit.workflow.interfaces.IWorkflow)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IWorkflow,
        'http://namespaces.zeit.de/CMS/workflow',
        ('edited', 'corrected', 'refined',
         'images_added', 'urgent'))
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflow['release_period'].fields[0],
        'http://namespaces.zeit.de/CMS/workflow',
        'released_from')
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflow['release_period'].fields[1],
        'http://namespaces.zeit.de/CMS/workflow',
        'released_until')

    def __init__(self, context):
        self.context = context
        self.resource = self.connector[context.uniqueId]

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)

    @property
    def properties(self):
        # check how write behaves...
        return LiveProperties(self.resource)

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_until

    @rwproperty.setproperty
    def release_period(self, value):
        if value is None:
            value = None, None
        self.released_from, self.released_until = value


@zope.component.adapter(zeit.workflow.interfaces.IWorkflow)
@zope.interface.implementer(zeit.cms.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return context.properties
