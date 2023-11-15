from functools import total_ordering
import zeit.cms.interfaces
import zope.app.keyreference.interfaces
import zope.component
import zope.interface


@total_ordering
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zope.app.keyreference.interfaces.IKeyReference)
class CMSContentKeyReference:
    """An IKeyReference to cms objects."""

    key_type_id = 'zeit.cms.content.keyreference'

    def __init__(self, object):
        if object.uniqueId is None:
            raise zope.app.keyreference.interfaces.NotYet(object)
        # Special cases that keep piling up, sigh.
        renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(object, None)
        if renameable and renameable.renameable and renameable.rename_to:
            parent = zeit.cms.interfaces.ICMSContent(object.uniqueId).__parent__
            self.referenced_object = parent.uniqueId + renameable.rename_to
        else:
            self.referenced_object = object.uniqueId

    def __call__(self):
        return zeit.cms.interfaces.ICMSContent(self.referenced_object)

    def __hash__(self):
        return hash(self.referenced_object)

    def __eq__(self, other):
        return self.referenced_object == other.referenced_object

    def __gt__(self, other):
        if self.key_type_id > other.key_type_id:
            return True
        return self.referenced_object > other.referenced_object


class UniqueIdKeyReference(CMSContentKeyReference):
    def __init__(self, parent, name):
        self.referenced_object = parent.uniqueId + name
