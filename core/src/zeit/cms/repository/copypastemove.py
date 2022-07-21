import grokcore.component as grok
import zeit.cms.repository.interfaces
import zope.component
import zope.container.interfaces
import zope.copypastemove
import zope.lifecycleevent


@zope.component.adapter(zeit.cms.repository.interfaces.IRepositoryContent)
class CMSObjectMover(zope.copypastemove.ObjectMover):
    """Objectmover for ICMSContent."""

    def moveTo(self, target, new_name=None):
        obj = self.context

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        chooser = zope.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)
        target[new_name] = obj
        return new_name


@zope.component.adapter(zeit.cms.repository.interfaces.IRepositoryContent)
class CMSObjectCopier(zope.copypastemove.ObjectCopier):

    def copyTo(self, target, new_name=None):
        obj = self.context

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        chooser = zope.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        new = repository.getCopyOf(obj.uniqueId)
        del new.__parent__
        del new.__name__
        target[new_name] = new  # This actually copies.
        new = target[new_name]
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(new, obj))
        return new_name


@grok.subscribe(zeit.cms.repository.interfaces.IBeforeObjectRemovedEvent)
def delete_objectlog_on_delete(event):
    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    log.delete(event.object)


@grok.subscribe(
    zeit.cms.repository.interfaces.IRepositoryContent,
    zope.lifecycleevent.IObjectMovedEvent)
def delete_objectlog_on_move(context, event):
    if not all([event.oldParent, event.oldName]):
        return
    if zeit.cms.checkout.interfaces.IWorkingcopy.providedBy(event.newParent):
        return
    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    log.delete(zeit.cms.content.keyreference.UniqueIdKeyReference(
        event.oldParent, event.oldName))
