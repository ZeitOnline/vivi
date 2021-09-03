import copy
import logging
import pdb
import transaction

import zope.interface
import zope.security.proxy

import zeit.cms.celery
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces as Cinterfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces


log = logging.getLogger(__name__)


@zeit.cms.celery.task
def materialize_content(folder):
    log.info('Materialize {}'.format(folder.uniqueId))

    parent = zope.security.proxy.getObject(folder)
    virtual_content_keys = [key for key in parent.keys() if key not in [
                    parent.config_file.__name__,
                    parent.content_template_file.__name__
                ]]

    for key in virtual_content_keys:
        content = copy.copy(zope.security.proxy.getObject(parent[key]))
        repository_properties = Cinterfaces.IWebDAVReadProperties(parent[key])

        if DFinterfaces.IVirtualContent.providedBy(content):
            log.info('Materialize {}'.format(content.uniqueId))
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

        if DFinterfaces.IMaterializedContent.providedBy(content):
            log.info('{} was materialized before'.format(content.uniqueId))

    transaction.commit()
