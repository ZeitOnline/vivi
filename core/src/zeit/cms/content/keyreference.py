from functools import total_ordering

import zope.app.keyreference.interfaces
import zope.component
import zope.interface

import zeit.cms.interfaces


@total_ordering
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zope.app.keyreference.interfaces.IKeyReference)
class CMSContentKeyReference:
    """An IKeyReference to cms objects."""

    key_type_id = 'zeit.cms.content.keyreference'

    def __init__(self, object):
        uuid = zeit.cms.content.interfaces.IUUID(object)
        if uuid.shortened is None:
            raise zope.app.keyreference.interfaces.NotYet(object)
        self.referenced_object = uuid.shortened

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
