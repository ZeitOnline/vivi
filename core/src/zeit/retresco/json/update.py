import json
import logging
import zeit.cms.celery
import zeit.cms.content.contentuuid
import zeit.cms.content.interfaces
import zeit.retresco.update

log = logging.getLogger(__name__)


class UpdateKeywords(object):

    # A hopefully more correct version than zeit.cms.browser.view.JSON
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        status, message = self.update()
        self.request.response.setStatus(status)
        return json.dumps({'message': message})

    def update(self):
        if self.request.method != 'POST':
            return 405, 'Only POST supported'

        try:
            body = self.request.bodyStream.read(
                int(self.request['CONTENT_LENGTH']))
            doc_ids = json.loads(body)['doc_ids']
        except:
            message = (
                'JSON body with parameter doc_ids (list of uuids) required')
            return 400, message

        for doc_id in doc_ids:
            update_async.delay(doc_id)
        return 200, 'OK'


@zeit.cms.celery.task(queuename='search')
def update_async(uuid):
    try:
        content = zeit.cms.content.contentuuid.uuid_to_content(
            zeit.cms.content.interfaces.IUUID(uuid))
    except:
        log.warning('TMS wants to update invalid id %s, ignored', uuid)
    else:
        zeit.retresco.update.index(content, enrich=True, publish=True)
