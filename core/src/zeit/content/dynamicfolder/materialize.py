from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
from zeit.connector.interfaces import IWebDAVReadProperties
from zeit.connector.interfaces import IWebDAVWriteProperties
from zeit.content.dynamicfolder.interfaces import IMaterializedContent
from zeit.content.dynamicfolder.interfaces import IVirtualContent
import logging
import zeit.cms.celery
import zeit.cms.interfaces
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


def materialize_content(folder):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.dynamicfolder') or {}
    batch_size = config.get('materialized-publish-batch-size', 100)

    to_regenerate = []
    regenerate_count = 0
    to_materialize = []
    materialize_count = 0

    for content in folder.values():
        if IMaterializedContent.providedBy(content):
            to_regenerate.append(content.__name__)
            regenerate_count += 1
        if IVirtualContent.providedBy(content):
            to_materialize.append(content.__name__)
            materialize_count += 1
        if len(to_regenerate) >= batch_size:
            regenerate.delay(folder.uniqueId, to_regenerate)
            to_regenerate = []
        if len(to_materialize) >= batch_size:
            materialize.delay(folder.uniqueId, to_materialize)
            to_materialize = []

    if to_regenerate:
        regenerate.delay(folder.uniqueId, to_regenerate)
    if to_materialize:
        materialize.delay(folder.uniqueId, to_materialize)

    zeit.objectlog.interfaces.ILog(folder).log(
        _('Materialize ${materialize}, Regenerate ${regenerate}', mapping={
            'materialize': materialize_count, 'regenerate': regenerate_count}))


@zeit.cms.celery.task(queue='manual')
def materialize(folder_id, keys):
    folder = zeit.cms.interfaces.ICMSContent(folder_id)
    for key in keys:
        content = folder[key]
        log.info('Materialize %s', content.uniqueId)
        _materialize(content)
    zeit.objectlog.interfaces.ILog(folder).log(
        _('Materialized ${count}', mapping={'count': len(keys)}))


@zeit.cms.celery.task(queue='manual')
def regenerate(folder_id, keys):
    folder = zeit.cms.interfaces.ICMSContent(folder_id)
    for key in keys:
        del folder[key]
        content = folder[key]
        log.info('Regenerate %s', content.uniqueId)
        _materialize(content)
    zeit.objectlog.interfaces.ILog(folder).log(
        _('Regenerated ${count}', mapping={'count': len(keys)}))


def _materialize(content):
    repository_properties = IWebDAVReadProperties(content)

    zope.interface.alsoProvides(content, IMaterializedContent)
    zope.interface.noLongerProvides(content, IVirtualContent)

    folder = content.__parent__  # only available *with* IRepositoryContent
    zope.interface.noLongerProvides(content, IRepositoryContent)
    new_properties = IWebDAVWriteProperties(content)
    new_properties.update(repository_properties)
    content.__parent__ = folder
    folder[content.__name__] = content

    zeit.objectlog.interfaces.ILog(content).log(_('Materialized'))


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
            publish.publish_multiple(objects, priority='manual')
            objects = []
    # The folder itself does not actually need to be published, we're only
    # doing it for the objectlog message. Add it as the last object, so the
    # user can confirm when all publish tasks have completed.
    objects.append(folder)
    # This also handles any batch that may be remaining after the loop.
    publish.publish_multiple(objects, priority='manual')
    zeit.objectlog.interfaces.ILog(folder).log(
        _('About to publish ${count} objects', mapping={'count': count}))
