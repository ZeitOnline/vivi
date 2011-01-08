# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zope.app.keyreference.interfaces
import zope.component
import zope.interface


class CMSContentKeyReference(object):
    """An IKeyReference to cms objects."""

    zope.interface.implements(zope.app.keyreference.interfaces.IKeyReference)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    key_type_id = 'zeit.cms.content.keyreference'

    def __init__(self, object):
        if object.uniqueId is None:
            raise zope.app.keyreference.interfaces.NotYet(object)
        self.referenced_object = object.uniqueId

    def __call__(self):
        return zeit.cms.interfaces.ICMSContent(self.referenced_object)

    def __hash__(self):
        return hash(self.referenced_object)

    def __cmp__(self, other):
        v = cmp(self.key_type_id, other.key_type_id)
        if v:
            return v
        return cmp(self.referenced_object, other.referenced_object)
