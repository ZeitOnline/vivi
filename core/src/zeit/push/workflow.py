import logging

import grokcore.component as grok
import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushMessages)
class PushMessages(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('message_config',),
        writeable=WRITEABLE_ALWAYS,
        use_default=True,
    )

    zeit.cms.content.dav.mapProperties(
        zeit.push.interfaces.IPushMessages, zeit.workflow.interfaces.WORKFLOW_NS, ('short_text',)
    )

    @property
    def messages(self):
        result = []
        for config in self.message_config:
            if not config.get('enabled'):
                continue
            if config['type'] == 'mobile':
                continue
            result.append(self._create_message(config['type'], self.context, config))
        return result

    def _create_message(self, typ, content, config):
        message = zope.component.getAdapter(content, zeit.push.interfaces.IMessage, name=typ)
        message.config = config
        return message

    MISSING = object()

    def get(self, **query):
        for item in self.message_config:
            found = {key: item.get(key, self.MISSING) for key in query}
            if found == query:
                return item
        return None

    def set(self, query, **values):
        config = list(self.message_config)
        for item in config:
            found = {key: item.get(key, self.MISSING) for key in query}
            if found == query:
                item.update(values)
                break
        else:
            values.update(query)
            config.append(values)
        self.message_config = tuple(config)

    def delete(self, query):
        config = list(self.message_config)
        config.remove(query)
        self.message_config = tuple(config)


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_content_channel_from_template(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE
    channels = set()
    for config in push.message_config:
        if config.get('type') != 'mobile':
            continue
        if not config.get('enabled'):
            continue
        template = source.find(config.get('payload_template'))
        if template is None:
            continue
        for channel in template.channels:
            if channel not in context.channels:
                channels.add(channel)

    if channels:
        context.channels += tuple(channels)


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent)
def send_push_on_publish(context, event):
    """Send push notifications for each enabled service.

    Catch errors to process the remaining services, rather stopping entirely.
    However we don't expect errors here, since `IMessage` takes care of errors
    issued by the external service.

    """
    push = zeit.push.interfaces.IPushMessages(context)
    for message in push.messages:
        config = {
            key: value for key, value in message.config.items() if key not in ('type', 'enabled')
        }
        config['text'] = message.text
        try:
            message.send()
        except Exception as e:
            zeit.objectlog.interfaces.ILog(context).log(
                _(
                    'Error while sending ${type}: ${reason}',
                    mapping={'type': message.type.capitalize(), 'reason': str(e)},
                )
            )
            log.error('Error during push to %s with config %s', message.type, config, exc_info=True)
