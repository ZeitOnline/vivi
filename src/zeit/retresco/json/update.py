from zeit.retresco.update import index_async
import json
import logging
import zeit.cms.content.contentuuid
import zeit.cms.content.interfaces

log = logging.getLogger(__name__)


class UpdateKeywords(object):

    # A hopefully more correct version than zeit.cms.browser.view.JSON
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        status, result = self.update()
        self.request.response.setStatus(status)
        return json.dumps(result)

    def update(self):
        status = {
            'message': '',
            'invalid': [],
            'updated': [],
            'updated_content': [],
        }

        if self.request.method != 'POST':
            status['message'] = 'Only POST supported'
            return 405, status

        try:
            body = self.request.bodyStream.read(
                int(self.request['CONTENT_LENGTH']))
            doc_ids = json.loads(body)['doc_ids']
        except:
            status['message'] = (
                'JSON body with parameter doc_ids (list of uuids) required')
            return 400, status

        for doc_id in doc_ids:
            try:
                content = zeit.cms.content.contentuuid.uuid_to_content(
                    zeit.cms.content.interfaces.IUUID(doc_id))
                index_async(content.uniqueId, True, True)
                status['updated'].append(doc_id)
                status['updated_content'].append(content.uniqueId)
            except (AttributeError, TypeError):
                status['invalid'].append(doc_id)
                continue
            else:
                log.info('Scheduling %s for reindex', content.uniqueId)
        status['message'] = 'Nothing updated'
        if status['updated']:
            status['message'] = 'Update successful'
        return 200, status
