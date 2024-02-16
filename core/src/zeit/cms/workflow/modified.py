from datetime import datetime

import grokcore.component as grok
import pytz
import zope.dublincore.interfaces
import zope.interface

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


MIN_DATE = datetime.min.replace(tzinfo=pytz.UTC)


@grok.implementer(zeit.cms.workflow.interfaces.IModified)
class Modified(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_last_modified', 'last_modified_by', 'date_last_checkout'),
    )


@grok.subscribe(zope.interface.Interface, zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).last_modified_by = event.principal.id


@grok.subscribe(zope.interface.Interface, zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def update_date_last_checkout(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).date_last_checkout = datetime.now(pytz.UTC)


@grok.subscribe(zope.interface.Interface, zeit.cms.workflow.interfaces.IBeforePublishEvent)
def update_date_last_published_semantic(context, event):
    published = zeit.cms.workflow.interfaces.IPublishInfo(context)
    date_last_published_semantic = published.date_last_published_semantic or MIN_DATE
    lsc = zeit.cms.content.interfaces.ISemanticChange(context)
    last_semantic_change = lsc.last_semantic_change or MIN_DATE
    if last_semantic_change > date_last_published_semantic:
        published.date_last_published_semantic = published.date_last_published
