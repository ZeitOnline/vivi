from datetime import datetime

import grokcore.component as grok
import pendulum
import zope.interface

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.interfaces


MIN_DATE = pendulum.instance(datetime.min)


@grok.implementer(zeit.cms.workflow.interfaces.IModified)
class Modified(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_last_modified', 'last_modified_by', 'date_last_checkout', 'date_created'),
    )


class LocalModified(Modified):
    grok.context(zeit.cms.workingcopy.interfaces.ILocalContent)

    checkin = Modified.date_last_modified

    @property
    def date_last_modified(self):
        return self._zodb or self.checkin

    @property
    def _zodb(self):
        if self.context._p_mtime is None:
            return None
        return pendulum.from_timestamp(self.context._p_mtime)

    @date_last_modified.setter
    def date_last_modified(self, value):
        self.checkin = value


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zope.lifecycleevent.IObjectCreatedEvent)
def set_date_on_create(context, event):
    if zope.lifecycleevent.IObjectCopiedEvent.providedBy(event):
        return
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).date_created = pendulum.now()


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
    zope.security.proxy.removeSecurityProxy(modified).date_last_checkout = pendulum.now()


@grok.subscribe(zope.interface.Interface, zeit.cms.workflow.interfaces.IBeforePublishEvent)
def update_date_last_published_semantic(context, event):
    published = zeit.cms.workflow.interfaces.IPublishInfo(context)
    date_last_published_semantic = published.date_last_published_semantic or MIN_DATE
    lsc = zeit.cms.content.interfaces.ISemanticChange(context)
    last_semantic_change = lsc.last_semantic_change or MIN_DATE
    if last_semantic_change > date_last_published_semantic:
        published.date_last_published_semantic = published.date_last_published
