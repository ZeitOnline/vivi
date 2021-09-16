import transaction

from zeit.cms.i18n import MessageFactory as _

import zeit.cms.celery
import zeit.cms.interfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces
import zeit.objectlog.interfaces


@zeit.cms.celery.task
def publish_content(unique_id):
    folder = zeit.cms.interfaces.ICMSContent(unique_id)
    objects = []
    for key in folder.keys():
        if DFinterfaces.IMaterializedContent.providedBy(folder[key]):
            objects.append(folder[key])
    zeit.cms.workflow.interfaces.IPublish(
        folder).publish_multiple(objects)
    msg = _('Published')
    zeit.objectlog.interfaces.ILog(folder).log(msg)
    transaction.commit()
