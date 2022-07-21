from zeit.cms.content.interfaces import WRITEABLE_LIVE
import grokcore.component as grok
import os.path
import zeit.cms.checkout.interfaces
import zeit.cms.redirect.interfaces
import zeit.cms.relation.corehandlers
import zeit.cms.repository.interfaces
import zope.component
import zope.lifecycleevent


@zope.interface.implementer(zeit.cms.redirect.interfaces.IRenameInfo)
class RenameInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    zeit.cms.content.dav.mapProperties(
        zeit.cms.redirect.interfaces.IRenameInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('previous_uniqueIds',),
        writeable=WRITEABLE_LIVE, use_default=True)


@grok.subscribe(
    zeit.cms.repository.interfaces.IRepositoryContent,
    zope.lifecycleevent.IObjectMovedEvent)
def store_redirect(context, event):
    if not all([event.oldParent, event.newParent,
                event.oldName, event.newName]):
        return
    if zeit.cms.checkout.interfaces.IWorkingcopy.providedBy(event.newParent):
        return
    lookup = zope.component.getUtility(zeit.cms.redirect.interfaces.ILookup)
    old_id = os.path.join(event.oldParent.uniqueId, event.oldName)
    new_id = os.path.join(event.newParent.uniqueId, event.newName)
    lookup.rename(old_id, new_id)
    zeit.cms.redirect.interfaces.IRenameInfo(
        context).previous_uniqueIds += (old_id,)
    # We need to update objects referencing the old name.
    zeit.cms.relation.corehandlers.update_referencing_objects.delay(old_id)
