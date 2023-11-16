from io import BytesIO
from zeit.cms.i18n import MessageFactory as _
import persistent
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.content.text.interfaces
import zope.interface


@zope.interface.implementer(zeit.content.text.interfaces.IText, zeit.cms.interfaces.IAsset)
class Text(zeit.cms.repository.repository.ContentBase, persistent.Persistent):
    text = None

    zeit.cms.content.dav.mapProperties(
        zeit.content.text.interfaces.IText,
        zeit.content.text.interfaces.DAV_NAMESPACE,
        ('mimeType',),
        use_default=True,
    )


class TextType(zeit.cms.type.TypeDeclaration):
    interface = zeit.content.text.interfaces.IText
    type = 'text'
    title = _('Plain text')
    factory = Text
    addform = zeit.cms.type.SKIP_ADD

    def content(self, resource):
        data = resource.data.read()
        text = self.factory()
        text.uniqueId = resource.id
        text.text = data.decode('utf-8')
        return text

    def resource_body(self, content):
        if isinstance(content.text, str):
            return BytesIO(content.text.encode('utf-8'))
        else:
            return BytesIO(content.text)

    def resource_content_type(self, content):
        return 'text/plain'
