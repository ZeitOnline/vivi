from datetime import datetime

import pytz
import zope.component
import zope.dublincore.interfaces
import zope.interface

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


MIN_DATE = datetime.min.replace(tzinfo=pytz.UTC)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IModified)
class Modified(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('last_modified_by', 'date_last_checkout'),
    )

    @property
    def date_last_modified(self):
        dc = zope.dublincore.interfaces.IDCTimes(self.context, None)
        if dc is None:
            return None
        return dc.modified


@zope.component.adapter(zope.interface.Interface, zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).last_modified_by = event.principal.id


@zope.component.adapter(zope.interface.Interface, zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def update_date_last_checkout(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).date_last_checkout = datetime.now(pytz.UTC)


@zope.component.adapter(zope.interface.Interface, zeit.cms.workflow.interfaces.IBeforePublishEvent)
def update_date_last_published_semantic(context, event):
    published = zeit.cms.workflow.interfaces.IPublishInfo(context)
    date_last_published_semantic = published.date_last_published_semantic or MIN_DATE
    lsc = zeit.cms.content.interfaces.ISemanticChange(context)
    last_semantic_change = lsc.last_semantic_change or MIN_DATE
    if last_semantic_change > date_last_published_semantic:
        published.date_last_published_semantic = published.date_last_published
