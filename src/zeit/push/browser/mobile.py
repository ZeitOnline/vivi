from zope.cachedescriptors.property import Lazy as cachedproperty
import json
import logging
import sys
import zeit.content.text.jinja
import zeit.push.interfaces
import zope.component
import zope.security.proxy

log = logging.getLogger(__name__)


class FindTitle(object):

    def __call__(self):
        name = self.request.form.get('q')
        if not name:
            return ''
        template = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(
            name)
        try:
            result = template(zeit.content.text.jinja.MockDict())
            return json.loads(result)['default_title']
        except:
            log.debug('No default title for %s', name, exc_info=True)
            return ''


class PreviewPayload(object):

    @cachedproperty
    def message(self):
        # We need to talk to private API
        push = zope.security.proxy.getObject(
            zeit.push.interfaces.IPushMessages(self.context))
        return push._create_message(
            'mobile', self.context, push.get(type='mobile'))

    @cachedproperty
    def rendered(self):
        template = self.message.find_template(
            self.message.config.get('payload_template'))
        return template(self.message.template_variables)

    def rendered_linenumbers(self):
        result = []
        for i, line in enumerate(self.rendered.split('\n')):
            result.append(u'%03d %s' % (i, line))
        return '\n'.join(result)

    @cachedproperty
    def error(self):
        try:
            self.message.validate_template(self.rendered)
        except Exception, e:
            e.traceback = zeit.cms.browser.error.getFormattedException(
                sys.exc_info())
            return e
