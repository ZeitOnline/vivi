import json
import logging

import zope.app.appsetup.product

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.celery
import zeit.cms.content.contentuuid
import zeit.cms.content.interfaces
import zeit.objectlog.interfaces
import zeit.retresco.update


log = logging.getLogger(__name__)


class UpdateKeywords:
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
            body = self.request.bodyStream.read(int(self.request['CONTENT_LENGTH']))
            doc_ids = json.loads(body)['doc_ids']
        except Exception:
            message = 'JSON body with parameter doc_ids (list of uuids) required'
            return 400, message

        config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
        for doc_id in doc_ids:
            update_async.delay(doc_id, _principal_id_=config['index-principal'])
        return 200, 'OK'


@zeit.cms.celery.task(queue='tms')
def update_async(uuid):
    try:
        content = zeit.cms.content.contentuuid.uuid_to_content(
            zeit.cms.content.interfaces.IUUID(uuid)
        )
        if content is None:
            raise KeyError(uuid)
    except Exception:
        log.warning('TMS wants to update invalid id %s, ignored', uuid)
        return
    zeit.objectlog.interfaces.ILog(content).log(_('TMS reindex'))
    zeit.retresco.update.index(content, enrich=True, update_keywords=True, publish=True)
