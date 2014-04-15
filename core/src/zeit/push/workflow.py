from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
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
    if event.name in list(zeit.push.interfaces.IPushServices):
        event.veto()
