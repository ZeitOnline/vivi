import persistent
import zeit.cms.browser.interfaces
import zeit.cms.clipboard.interfaces
import zeit.cms.interfaces
import zope.app.container.contained
import zope.app.container.ordered
import zope.component
import zope.interface
import zope.publisher.browser


class Entry(zope.app.container.contained.Contained,
            persistent.Persistent):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.clipboard.interfaces.IObjectReference)

    title = None
    content_type = None

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

        list_repr = zope.component.queryMultiAdapter(
            (references, self._request),
            zeit.cms.browser.interfaces.IListRepresentation)
        if list_repr is not None and list_repr.title:
            self.title = list_repr.title
        self.content_type = zeit.cms.type.get_type(references) or ''

    @property
    def referenced_unique_id(self):
        return self._value

    _request = zope.publisher.browser.TestRequest(
        skin=zeit.cms.browser.interfaces.ICMSLayer)


@zope.component.adapter(zeit.cms.clipboard.interfaces.IClipboardEntry)
@zope.interface.implementer(zeit.cms.clipboard.interfaces.IClipboard)
def entry_to_clipboard(context):
    return zeit.cms.clipboard.interfaces.IClipboard(context.__parent__)


class Clip(zope.app.container.ordered.OrderedContainer):

    zope.interface.implements(zeit.cms.clipboard.interfaces.IClip)

    def __init__(self, title):
        super(Clip, self).__init__()
        self.title = title
