import logging
import json
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
            return json.loads(template.text)['default_title']
        except:
            log.debug('No default title for %s', name, exc_info=True)
            return ''
