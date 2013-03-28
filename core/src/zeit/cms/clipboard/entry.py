# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import zeit.cms.clipboard.interfaces
import zeit.cms.interfaces
import zope.app.container.contained
import zope.app.container.ordered
import zope.component
import zope.interface


class Entry(zope.app.container.contained.Contained,
            persistent.Persistent):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.clipboard.interfaces.IObjectReference)

    def __init__(self, references):
        self.references = references

    @property
    def references(self):
        return zeit.cms.interfaces.ICMSContent(self._value, None)

    @references.setter
    def references(self, references):
        if not zeit.cms.interfaces.ICMSContent.providedBy(references):
            raise TypeError("Referenced object must provide ICMSContent.")
        uid = references.uniqueId
        if not uid:
            raise ValueError("Referenced object must have a uniqueid.")
        self._value = uid

    @property
    def referenced_unique_id(self):
        return self._value


@zope.component.adapter(zeit.cms.clipboard.interfaces.IClipboardEntry)
@zope.interface.implementer(zeit.cms.clipboard.interfaces.IClipboard)
def entry_to_clipboard(context):
    return zeit.cms.clipboard.interfaces.IClipboard(context.__parent__)


class Clip(zope.app.container.ordered.OrderedContainer):

    zope.interface.implements(zeit.cms.clipboard.interfaces.IClip)

    def __init__(self, title):
        super(Clip, self).__init__()
        self.title = title
