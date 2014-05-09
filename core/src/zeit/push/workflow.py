from datetime import datetime
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.objectlog.interfaces
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

    services.enabled = False


def send_push_notification(content, service):
    url = content.uniqueId.replace(
        zeit.cms.interfaces.ID_NAMESPACE, 'http://www.zeit.de/')
    notifier = zope.component.getUtility(
        zeit.push.interfaces.IPushNotifier, name=service)
    # XXX Make title configurable or read from content?
    notifier.send(content.title, url, title=u'Eilmeldung')
    zeit.objectlog.interfaces.ILog(content).log('Push to "%s"' % service)
    services = zeit.push.interfaces.IPushServices(content)
    services.date_last_pushed = datetime.now(pytz.UTC)
