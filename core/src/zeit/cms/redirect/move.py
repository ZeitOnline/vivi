import grokcore.component as grok
import zeit.cms.redirect.interfaces
import zeit.cms.repository.interfaces
import zope.component
import zope.lifecycleevent.interfaces


@grok.subscribe(
    zeit.cms.repository.interfaces.IRepositoryContent,
    zope.lifecycleevent.interfaces.IObjectMovedEvent)
def store_redirect(context, event):
    if not all([event.oldParent, event.newParent,
                event.oldName, event.newName]):
        return
    lookup = zope.component.getUtility(zeit.cms.redirect.interfaces.ILookup)
    lookup.rename(event.oldParent.uniqueId + event.oldName,
                  event.newParent.uniqueId + event.newName)
