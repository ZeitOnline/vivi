from zeit.cms.i18n import MessageFactory as _
import persistent
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.cms.util
import zope.interface


@zope.interface.implementer(
    zeit.cms.repository.interfaces.IUnknownResource, zeit.cms.content.interfaces.ITextContent
)
class UnknownResource(zeit.cms.repository.repository.ContentBase):
    """Represent an unknown resource"""

    def __init__(self, data, type_info=None):
        if not isinstance(data, str):
            raise TypeError('data must be unicode.')
        self.data = data
        self.type = type_info


class PersistentUnknownResource(UnknownResource, persistent.Persistent):
    """An unknown resource that is also persistent.

    We create a new class for this to be backward compatible. Just adding
    persistent.Persistent above will yield an error:

        TypeError: ('object.__new__(UnknownResource) is not safe,
            use persistent.Persistent.__new__()',
            <function _reconstructor at 0x1995f0>,
            (<class 'zeit.cms.repository.unknown.UnknownResource'>,
            <type 'object'>, None))

    """


class UnknownResourceType(zeit.cms.type.TypeDeclaration):
    type = 'unknown'
    title = _('Unknown Resource')
    interface = zeit.cms.repository.interfaces.IUnknownResource
    addform = zeit.cms.type.SKIP_ADD
    factory = PersistentUnknownResource

    def content(self, resource):
        return self.factory(resource.data.read().decode('latin1'), resource.type)

    def resource_body(self, content):
        return zeit.cms.util.MemoryFile(content.data.encode('latin1'))
