from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
from zeit.connector.interfaces import IWebDAVReadProperties
from zeit.connector.interfaces import IWebDAVWriteProperties
from zeit.content.dynamicfolder.interfaces import IMaterializedContent
from zeit.content.dynamicfolder.interfaces import IVirtualContent
import logging
import transaction
import zeit.cms.celery
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.objectlog.interfaces
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(
    zeit.content.dynamicfolder.interfaces.ICloneArmy)
class CloneArmy(zeit.cms.content.dav.DAVPropertiesAdapter):

    activate = zeit.cms.content.dav.DAVProperty(
        zeit.content.dynamicfolder.interfaces.ICloneArmy['activate'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'materializeable',
        writeable=WRITEABLE_ALWAYS
    )


@zeit.cms.celery.task
def materialize_content(unique_id):
    log.info('Materialize {}'.format(unique_id))
    msg = _('Materialized')
    parent = zeit.cms.interfaces.ICMSContent(unique_id)
    virtual_content_keys = [key for key in parent.keys() if key not in [
        parent.config_file.__name__,
        parent.content_template_file.__name__
    ]]

    regenerate = []
    materialize = []

    for key in virtual_content_keys:
        content = parent[key]

        if IMaterializedContent.providedBy(content):
            regenerate.append(key)
            log.info('{} is going to be regenerated'.format(content.uniqueId))

        if IVirtualContent.providedBy(content):
            materialize.append(key)

    for key in regenerate:
        materialize.append(key)
        del parent[key]
        transaction.commit()

    for key in materialize:
        content = parent[key]
        repository_properties = IWebDAVReadProperties(content)

        zope.interface.alsoProvides(content, IMaterializedContent)
        zope.interface.noLongerProvides(content, IVirtualContent)
        zope.interface.noLongerProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)

        new_properties = IWebDAVWriteProperties(content)
        new_properties.update(repository_properties)
        parent[key] = content

        log.info('Materialize {}'.format(content.uniqueId))
        zeit.objectlog.interfaces.ILog(content).log(msg)

    zeit.objectlog.interfaces.ILog(parent).log(msg)

    transaction.commit()


def publish_content(folder):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.dynamicfolder') or {}
    batch_size = config.get('materialized-publish-batch-size', 100)
    publish = zeit.cms.workflow.interfaces.IPublish(folder)
    count = 0
    objects = []
    for item in folder.values():
        if IMaterializedContent.providedBy(item):
            count += 1
            objects.append(item)
        if len(objects) >= batch_size:
            publish.publish_multiple(objects)
            objects.clear()
    if objects:
        publish.publish_multiple(objects)
    zeit.objectlog.interfaces.ILog(folder).log(
        _('About to publish ${count} objects', mapping={'count': count}))
