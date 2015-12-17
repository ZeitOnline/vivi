from datetime import datetime
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS, WRITEABLE_LIVE
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
    push = zeit.push.interfaces.IPushMessages(context)
    for message in push.messages:
        config = {key: value for key, value in message.config.items()
                  if key not in ('type', 'enabled')}
        config['text'] = message.text
        log_msg = 'Push "%s": %s' % (message.type, config)
        try:
            message.send()
        except Exception, e:
            log.error('Error during push to %s(%s)', message.type, config,
                      exc_info=True)
            log_msg += ' error: %s' % str(e)
        zeit.objectlog.interfaces.ILog(context).log(log_msg)

    push.date_last_pushed = datetime.now(pytz.UTC)
