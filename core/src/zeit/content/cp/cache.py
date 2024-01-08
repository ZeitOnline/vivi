import logging

import transaction

import zeit.cms.celery
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces


log = logging.getLogger(__name__)


@zeit.cms.celery.task
def prewarm_cache(uniqueId):
    content = zeit.cms.interfaces.ICMSContent(uniqueId)
    log.info('Prewarming %s', content.uniqueId)
    todo = [content]

    if zeit.content.cp.interfaces.ICenterPage.providedBy(content):
        for item in zeit.content.cp.interfaces.ITeaseredContent(content):
            todo.append(item)
            log.info('Found teaser %s', item.uniqueId)

            img = zeit.content.image.interfaces.IImages(item, None)
            img = getattr(img, 'image', None)
            if img is not None:
                todo.append(img)
                log.info('Found image %s', img.uniqueId)

            if zeit.cms.content.interfaces.ICommonMetadata.providedBy(item):
                for x in item.authorships:
                    if x.target:
                        todo.append(x.target)
                        log.info('Found author %s', x.target.uniqueId)

            transaction.commit()
    elif zeit.cms.repository.interfaces.IFolder.providedBy(content):
        for child in content.values():
            log.info('Found child %s', child)
            transaction.commit()

    # Explicitly resolve parents, zeit.cms.repository.repository.ContentBase
    for item in todo:
        while item.uniqueId != zeit.cms.interfaces.ID_NAMESPACE:
            item = item.__parent__
            log.info('Found parent %s', item.uniqueId)
            transaction.commit()
