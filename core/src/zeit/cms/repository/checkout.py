import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.component
import zope.copypastemove.interfaces
import zope.interface


@grok.adapter(zeit.cms.repository.interfaces.IDAVContent)
@grok.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def default_local_content_adapter(context):
    # Default adapter to adapt cms content to local content: create a copy and
    # mark as local content
    if zeit.cms.repository.interfaces.ICollection.providedBy(context):
        # We cannot checkout containers. Special treat is required for them.
        return None
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    try:
        content = repository.getCopyOf(context.uniqueId)
    except (ValueError, KeyError):
        return None
    repository_properties = zeit.connector.interfaces.IWebDAVProperties(context)
    zope.interface.alsoProvides(content, zeit.cms.workingcopy.interfaces.ILocalContent)
    assert not zeit.cms.repository.interfaces.IRepositoryContent.providedBy(content)
    new_properties = zeit.connector.interfaces.IWebDAVProperties(content)
    new_properties.update(repository_properties)
    return content


def add_to_repository(context, ignore_conflicts):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(context)
    if renameable.renameable and renameable.rename_to:
        rename_to = renameable.rename_to
        # Remove the attributes so we don't clutter the dav.
        renameable.renameable = None
        renameable.rename_to = None
    else:
        rename_to = None

    repository.addContent(context, ignore_conflicts)
    added = repository.getContent(context.uniqueId)
    if rename_to:
        mover = zope.copypastemove.interfaces.IObjectMover(added)
        rename_to = mover.moveTo(added.__parent__, rename_to)
        added = added.__parent__[rename_to]

    return added


@grok.adapter(zeit.cms.repository.interfaces.IDAVContent)
@grok.implementer(zeit.cms.checkout.interfaces.IRepositoryContent)
def default_repository_content_adapter(context):
    # Default adapter to adapt local content to repository content: add to
    # repository and return
    return add_to_repository(context, False)


@grok.adapter(zeit.cms.repository.interfaces.IDAVContent, name='non-conflicting')
@grok.implementer(zeit.cms.checkout.interfaces.IRepositoryContent)
def default_repository_content_adapter_non_conflicting(context):
    # Default adapter to adapt local content to repository content: add to
    # repository and return
    return add_to_repository(context, True)


@grok.implementer(zeit.cms.repository.interfaces.IAutomaticallyRenameable)
class AutomaticallyRenameable(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.adapts(zeit.cms.repository.interfaces.IDAVContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.repository.interfaces.IAutomaticallyRenameable,
        'http//namespaces.zeit.de/CMS/meta',
        ('renameable', 'rename_to'),
    )

    @property
    def uniqueId(self):
        return self.context.uniqueId
