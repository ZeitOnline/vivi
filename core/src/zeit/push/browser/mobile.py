from zope.cachedescriptors.property import Lazy as cachedproperty
import logging
import sys
import zeit.push.interfaces
import zope.security.proxy

log = logging.getLogger(__name__)


class FindTitle:

    def __call__(self):
        name = self.request.form.get('q')
        if not name:
            return ''
        source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
        template = source.find(name)
        return source.getDefaultTitle(template)


class PreviewPayload:

    @cachedproperty
    def message(self):
        # We need to talk to private API
        push = zope.security.proxy.getObject(
            zeit.push.interfaces.IPushMessages(self.context))
        return push._create_message(
            'mobile', self.context, push.get(type='mobile'))

    @cachedproperty
    def rendered(self):
        return self.message._render()

    def rendered_linenumbers(self):
        result = []
        for i, line in enumerate(self.rendered.split('\n')):
            result.append('%03d %s' % (i, line))
        return '\n'.join(result)

    @cachedproperty
    def error(self):
        try:
            self.message.validate_template(self.rendered)
        except Exception as e:
            e.traceback = zeit.cms.browser.error.getFormattedException(
                sys.exc_info())
            return e
