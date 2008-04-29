# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import UserDict
import datetime

import pytz
import rwproperty
import transaction

import zope.component
import zope.event
import zope.interface
import zope.location.location

import z3c.flashmessage.interfaces

import zeit.connector.interfaces
import zeit.objectlog.interfaces

import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.workflow.interfaces


if 'all' not in globals():
    # Python 2.4 doesn't have `all` :(
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True


WORKFLOW_NS = u'http://namespaces.zeit.de/CMS/workflow'


class Workflow(object):
    """Adapt ICMSContent to IWorkflow using the "live" data from connector.

    We must read and write properties directly from the DAV to be sure we
    actually can do the transition.
    """

    zope.interface.implements(zeit.workflow.interfaces.IWorkflowStatus)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IWorkflowStatus,
        WORKFLOW_NS,
        ('edited', 'corrected', 'refined', 'published',
         'images_added', 'urgent', 'date_last_published'),
        live=True)

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflowStatus['release_period'].fields[0],
        WORKFLOW_NS, 'released_from', live=True)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflowStatus['release_period'].fields[1],
        WORKFLOW_NS, 'released_to', live=True)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IWorkflowStatus,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, ('date_first_released',),
        live=True)

    def __init__(self, context):
        self.context = context

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_to

    @rwproperty.setproperty
    def release_period(self, value):
        if value is None:
            value = None, None
        self.released_from, self.released_to = value

    def can_publish(self):
        if self.urgent:
            return True
        if all([self.edited, self.corrected, self.refined, self.images_added]):
            return True
        return False


@zope.component.adapter(Workflow)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


class FeedMetadataUpdater(object):
    """Add the expire/publication time to feed entry."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def update_entry(self, entry, content):
        workflow = zeit.workflow.interfaces.IWorkflowStatus(content, None)
        if workflow is None:
            return

        date = ''
        if workflow.released_from:
            date = workflow.released_from.isoformat()
        entry.set('publication-date', date)

        date = ''
        if workflow.released_to:
            date = workflow.released_to.isoformat()
        entry.set('expires', date)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def set_first_release_date(context, event):
    workflow = zeit.workflow.interfaces.IWorkflowStatus(context)
    if workflow.date_first_released:
        return
    workflow.date_first_released = datetime.datetime.now(pytz.UTC)


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def copy_properties_to_xml(context, event):
    """There are some special properties which need to be in the xml.
    """
    # We act, when a property is changed *directly* on an IRepositoryContent.
    if not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
        context):
        return
    #if ((event.property_name, event.property_namespace) !=
    #    ('date_first_released', WORKFLOW_NS)):
    #    return
    manager = zeit.cms.checkout.interfaces.ICheckoutManager(context)
    if not manager.canCheckout:
        return
    checked_out = manager.checkout()

    # Nothing special happens here because checkout/checkin will copy the
    # properties.

    manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
    if not manager.canCheckin:
        del checked_out.__parent__[checked_out.__name__]
        return
    manager.checkin()


@zope.component.adapter(
    Workflow,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def log_workflow_changes(workflow, event):
    if event.field.__name__ not in ('edited', 'corrected', 'refined',
                                    'images_added', 'urgent'):
        # Only act on certain fields.
        return

    content = workflow.context
    message = _('${name}: ${new_value}',
                mapping=dict(name=event.field.title,
                             old_value=event.old_value,
                             new_value=event.new_value))

    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    log.log(content, message)
