from datetime import datetime
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS, WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import logging
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zope.interface


log = logging.getLogger(__name__)


class PushMessages(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.push.interfaces.IPushMessages)

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('message_config',),
        writeable=WRITEABLE_ALWAYS, use_default=True)

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        # BBB long_text now in message_config for individual facebook accounts
        ('long_text', 'short_text'))

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('date_last_pushed',), writeable=WRITEABLE_LIVE)

    @property
    def messages(self):
        result = []
        for config in self.message_config:
            if not config.get('enabled'):
                continue
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
    """Send push notifications for each enabled service.

    Catch errors to process the remaining services, rather stopping entirely.
    However we don't expect errors here, since `IMessage` takes care of errors
    issued by the external service.

    """
    push = zeit.push.interfaces.IPushMessages(context)
    for message in push.messages:
        config = {key: value for key, value in message.config.items()
                  if key not in ('type', 'enabled')}
        config['text'] = message.text
        try:
            message.send()
        except Exception, e:
            zeit.objectlog.interfaces.ILog(context).log(_(
                'Error while sending ${type}: ${reason}',
                mapping={'type': message.type.capitalize(), 'reason': str(e)}))
            log.error('Error during push to %s with config %s',
                      message.type, config, exc_info=True)

    push.date_last_pushed = datetime.now(pytz.UTC)
