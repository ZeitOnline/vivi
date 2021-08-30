import copy
import pdb
import transaction

import zope.interface
import zope.security.proxy

import zeit.cms.celery
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces as Cinterfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces


# @zeit.cms.celery.task
def materialize_content(folder):

    virtual_content_keys = [key for key in folder.keys() if key not in [
                    folder.config_file.__name__,
                    folder.content_template_file.__name__
                ]]
    for key in virtual_content_keys:
        content = copy.copy(zope.security.proxy.getObject(folder[key]))
        repository_properties = Cinterfaces.IWebDAVReadProperties(
            folder[key])

        if DFinterfaces.IVirtualContent.providedBy(content):
            zope.interface.alsoProvides(
                content, DFinterfaces.IMaterializedContent)
            zope.interface.noLongerProvides(
                content, DFinterfaces.IVirtualContent)
            new_properties = Cinterfaces.IWebDAVWriteProperties(content)
            new_properties.update(repository_properties)

            folder[key] = content

        if DFinterfaces.IMaterializedContent.providedBy(content):
            modified = zeit.cms.workflow.interfaces.IModified(content)
