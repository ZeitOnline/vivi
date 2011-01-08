# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.component
import zope.copypastemove.interfaces
import zope.interface


@grokcore.component.adapter(zeit.cms.repository.interfaces.IDAVContent)
@grokcore.component.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def default_local_content_adapter(context):
    # Default adapter to adapt cms content to local content: create a copy and
    # mark as local content
    if zeit.cms.repository.interfaces.ICollection.providedBy(context):
        # We cannot checkout containers. Special treat is required for them.
        return None
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        content = repository.getCopyOf(context.uniqueId)
    except (ValueError, KeyError):
        return None
    repository_properties = zeit.connector.interfaces.IWebDAVProperties(
        context)
    zope.interface.alsoProvides(
        content, zeit.cms.workingcopy.interfaces.ILocalContent)
    assert not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
        content)
    new_properties = zeit.connector.interfaces.IWebDAVProperties(content)
    new_properties.update(repository_properties)
    return content


def add_to_repository(context, ignore_conflicts):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    renamable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(
        context)
    if renamable.renamable and renamable.rename_to:
        rename_to = renamable.rename_to
        # Remove the attributes so we don't clutter the dav.
        renamable.renamable = None
        renamable.rename_to = None
    else:
        rename_to = None

    repository.addContent(context, ignore_conflicts)
    added = repository.getContent(context.uniqueId)
    if rename_to:
        mover = zope.copypastemove.interfaces.IObjectMover(added)
        rename_to = mover.moveTo(added.__parent__, rename_to)
        added = added.__parent__[rename_to]

    return added


@grokcore.component.adapter(zeit.cms.repository.interfaces.IDAVContent)
@grokcore.component.implementer(
    zeit.cms.checkout.interfaces.IRepositoryContent)
def default_repository_content_adapter(context):
    # Default adapter to adapt local content to repository content: add to
    # repository and return
    return add_to_repository(context, False)


@grokcore.component.adapter(zeit.cms.repository.interfaces.IDAVContent,
                            name=u'non-conflicting')
@grokcore.component.implementer(
    zeit.cms.checkout.interfaces.IRepositoryContent)
def default_repository_content_adapter_non_conflicting(context):
    # Default adapter to adapt local content to repository content: add to
    # repository and return
    return add_to_repository(context, True)


class AutomaticallyRenamable(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.adapts(zeit.cms.repository.interfaces.IDAVContent)
    grokcore.component.implements(
        zeit.cms.repository.interfaces.IAutomaticallyRenameable)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.repository.interfaces.IAutomaticallyRenameable,
        'http//namespaces.zeit.de/CMS/meta',
        ('renamable', 'rename_to'))
