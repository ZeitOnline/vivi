# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
import pytz
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.interface


MIN_DATE = datetime.min.replace(tzinfo=pytz.UTC)


class Modified(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.workflow.interfaces.IModified)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('last_modified_by', ))

    @property
    def date_last_modified(self):
        dc = zope.dublincore.interfaces.IDCTimes(self.context, None)
        if dc is not None:
            return dc.modified


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).last_modified_by = (
        event.principal.id)


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def update_date_last_published_semantic(context, event):
    published = zeit.cms.workflow.interfaces.IPublishInfo(context)
    date_last_published_semantic = (
        published.date_last_published_semantic or MIN_DATE)
    lsc = zeit.cms.content.interfaces.ISemanticChange(context)
    last_semantic_change = lsc.last_semantic_change or MIN_DATE
    if last_semantic_change > date_last_published_semantic:
        published.date_last_published_semantic = datetime.now(pytz.UTC)
