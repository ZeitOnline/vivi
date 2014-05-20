from datetime import datetime
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zope.interface


class PushMessages(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.push.interfaces.IPushMessages)

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('enabled', 'message_config'),
        writeable=WRITEABLE_ALWAYS, use_default=True)

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('date_last_pushed', 'long_text', 'short_text'),
        writeable=WRITEABLE_ALWAYS)

    @property
    def messages(self):
        result = []
        for config in self.message_config:
            result.append(
                self._create_message(config['type'], self.context, config))
        return result

    def _create_message(self, typ, content, config):
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name=typ)
        message.config = config
        return message


@grok.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_push_properties(event):
    if event.name == 'message_config':
        event.veto()


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def send_push_on_publish(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    if not push.enabled:
        return

    for message in push.messages:
        zeit.objectlog.interfaces.ILog(context).log(
            'Push to "%s", %s' % (message.type, message.config))
        message.send()

    push.date_last_pushed = datetime.now(pytz.UTC)
    push.enabled = False
