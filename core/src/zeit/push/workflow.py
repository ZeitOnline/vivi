from datetime import datetime
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.workflow.interfaces
import zope.interface


class PushServices(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.push.interfaces.IPushServices)

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushServices,
        zeit.workflow.interfaces.WORKFLOW_NS,
        list(zeit.push.interfaces.IPushServices),
        writeable=WRITEABLE_ALWAYS, use_default=True)


@grok.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_push_properties(event):
    if event.name in zeit.push.interfaces.PUSH_SERVICES:
        event.veto()


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def send_push_on_publish(context, event):
    services = zeit.push.interfaces.IPushServices(context)
    if not services.enabled:
        return

    for service in zeit.push.interfaces.PUSH_SERVICES:
        if getattr(services, service):
            send_push_notification(context, service)


def send_push_notification(content, service):
    url = content.uniqueId.replace(
        zeit.cms.interfaces.ID_NAMESPACE, 'http://www.zeit.de/')
    notifier = zope.component.getUtility(
        zeit.push.interfaces.IPushNotifier, name=service)
    notifier.send(content.title, url)
    services = zeit.push.interfaces.IPushServices(content)
    services.date_last_pushed = datetime.now(pytz.UTC)


# XXX This is for the old system only, remove once VIV-25 is fully implemented.
@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def push_to_parse_legacy_eilmeldung(context, event):
    if context.uniqueId != 'http://xml.zeit.de/eilmeldung/eilmeldung':
        return
    services = zeit.push.interfaces.IPushServices(context)
    info = zeit.cms.workflow.interfaces.IPublishInfo(context)
    if services.date_last_pushed >= info.date_last_published:
        return

    notifier = zope.component.getUtility(
        zeit.push.interfaces.IPushNotifier, name='parse')
    notifier.send(context.xml.body.division.p.text, 'http://www.zeit.de/')
    services.date_last_pushed = datetime.now(pytz.UTC)
