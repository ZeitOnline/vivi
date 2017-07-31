import json
import logging
import zeit.content.text.jinja
import zeit.push.interfaces

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
