import transaction

import zeit.cms.celery
import zeit.cms.interfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces


@zeit.cms.celery.task
def publish_content(unique_id):
    folder = zeit.cms.interfaces.ICMSContent(unique_id)
    objects = []
    for key in folder.keys():
        if DFinterfaces.IMaterializedContent.providedBy(folder[key]):
            objects.append(folder[key])
    zeit.cms.workflow.interfaces.IPublish(
        folder).publish_multiple(objects)
    transaction.commit()
