# coding: utf-8
import json
import logging
import urllib.parse

import grokcore.component as grok
import zope.interface
import zope.lifecycleevent

import zeit.cms.config
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message


log = logging.getLogger(__name__)


class Message(zeit.push.message.Message):
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')
    type = 'urbanairship'

    APP_IDENTIFIER = 'zeitapp'

    def render(self):
        return self.validate_template(self._render())

    def send(self):
        """Sending to urbainairship is job of the Publisher"""

    def _render(self):
        template = self.find_template(self.config.get('payload_template'))
        return template(self.template_variables, output_format='json')

    @property
    def template_variables(self):
        result = self.config.copy()
        for key in ['enabled', 'override_text', 'type']:
            result.pop(key, None)
        result.update(
            {
                'article': self.context,
                'text': self.text,
                'zon_link': self.url,
                'app_link': self.app_link,
                'image': self.image_url,
                'uuid': zeit.cms.content.interfaces.IUUID(self.context).shortened,
            }
        )
        return result

    def validate_template(self, text):
        # If not proper json, a pretty good ValueError will be raised here.
        result = json.loads(text, strict=False)
        # XXX Maybe use the urbanairship python module validation API.
        return result['messages']

    def find_template(self, name):
        source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE
        template = source.find(name)
        if template is None:
            raise KeyError('Could not find template %r in %s' % (name, source.folder.uniqueId))
        return template

    @property
    def text(self):
        return self.config.get('override_text', self.context.title)

    @property
    def image_url(self):
        image = self.config.get('image')
        if not image:
            return None
        url = zeit.cms.config.required('zeit.push', 'mobile-image-url')
        return image.replace(zeit.cms.interfaces.ID_NAMESPACE, url)

    @property
    def app_link(self):
        parts = urllib.parse.urlparse(self.url)
        path = urllib.parse.urlunparse(['', ''] + list(parts[2:])).lstrip('/')
        return '%s://%s' % (self.APP_IDENTIFIER, path)

    @property
    def log_message_details(self):
        return 'Template %s' % self.config.get('payload_template')

    def log_success(self):
        super().log_success()
        try:
            grafana = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, name='grafana')
            grafana.send(self.text, self.url, **self.config)
        except Exception:
            log.warning('Error in log_success for %s', self.url, exc_info=True)
