from zeit.retresco.update import index_async
import json
import logging
import zeit.cms.browser.view

log = logging.getLogger(__name__)


class UpdateKeywords(zeit.cms.browser.view.Base):

    def __call__(self):
        if (self.request.method == 'POST' and
                not self.request.form.get('_body_decoded')):
            decoded = self.request.bodyStream.read(
                int(self.request['CONTENT_LENGTH']))

            try:
                for doc_id in json.loads(decoded).get('doc_ids'):
                    try:
                        content = zeit.cms.content.contentuuid.uuid_to_content(
                            zeit.cms.content.interfaces.IUUID(doc_id))
                        index_async(content.uniqueId)
                    except (AttributeError, TypeError):
                        log.warning('Error invalid UUID %s', doc_id,
                                    exc_info=True)
                        self.request.response.setStatus(422)
                        return json.dumps({"update": False})
            except (TypeError, ValueError):
                log.warning('Request invalid', exc_info=True)
                self.request.response.setStatus(400)
                return json.dumps({"update": False})

            log.info('Update successful')
            return json.dumps({"update": True})

        else:
            log.warning('Request invalid')
            self.request.response.setStatus(400)
            return json.dumps({"update": False})
