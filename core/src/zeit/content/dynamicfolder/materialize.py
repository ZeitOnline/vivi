import copy
import logging
import transaction

import zope.interface
import zope.security.proxy

from zeit.cms.i18n import MessageFactory as _

import zeit.cms.celery
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces as Cinterfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces
import zeit.objectlog.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(
    zeit.content.dynamicfolder.interfaces.ICloneArmy)
class CloneArmy(zeit.cms.content.dav.DAVPropertiesAdapter):

    activate = zeit.cms.content.dav.DAVProperty(
        DFinterfaces.ICloneArmy['activate'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'materializeable'
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
    objects_to_retract = []
    materialize = []

    for key in virtual_content_keys:
        content = copy.copy(zope.security.proxy.getObject(parent[key]))

        if DFinterfaces.IMaterializedContent.providedBy(content):
            regenerate.append(key)
            objects_to_retract.append(content)
            log.info('{} is going to be regenerated'.format(content.uniqueId))

        if DFinterfaces.IVirtualContent.providedBy(content):
            materialize.append(key)

    if regenerate:
        for key in regenerate:
            materialize.append(key)
            del parent[key]
            transaction.commit()

    parent = zeit.cms.interfaces.ICMSContent(unique_id)
    if materialize:
        for key in materialize:
            content = copy.copy(zope.security.proxy.getObject(parent[key]))
            repository_properties = Cinterfaces.IWebDAVReadProperties(
                parent[key])

            zope.interface.alsoProvides(
                content, DFinterfaces.IMaterializedContent)
            zope.interface.noLongerProvides(
                content, DFinterfaces.IVirtualContent)
            zope.interface.alsoProvides(
                content, zeit.cms.workingcopy.interfaces.ILocalContent)
            zope.interface.noLongerProvides(
                content, zeit.cms.repository.interfaces.IRepositoryContent)

            new_properties = Cinterfaces.IWebDAVWriteProperties(content)
            new_properties.update(repository_properties)
            parent[key] = content

            log.info('Materialize {}'.format(content.uniqueId))
            zeit.objectlog.interfaces.ILog(content).log(msg)

    zeit.objectlog.interfaces.ILog(parent).log(msg)

    transaction.commit()
