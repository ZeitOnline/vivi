import zope.annotation
import zope.component
import zope.securitypolicy.interfaces

import zeit.cms.content.template
import zeit.cms.repository.interfaces
import zeit.cms.generation
import zeit.connector.interfaces


def update(root):
    # Update templates to use special property class
    for container in root['templates'].values():
        for template in container.values():
            annotations = zope.annotation.interfaces.IAnnotations(template)
            old_properties = annotations.pop(
                'zeit.cms.content.adapter.webDAVPropertiesFactory', None
            )
            if old_properties is None:
                continue
            new_properties = zeit.connector.interfaces.IWebDAVProperties(template)
            new_properties.update(old_properties)

    # Revoke zope.ManageContent from zeit.Editor. This was used so editors
    # could lock/unlock. Solved differently now.
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    rpm = zope.securitypolicy.interfaces.IRolePermissionManager(repository)
    rpm.unsetPermissionFromRole('zope.ManageContent', 'zeit.Editor')


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
