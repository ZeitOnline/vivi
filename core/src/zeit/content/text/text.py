from io import BytesIO
from zeit.cms.i18n import MessageFactory as _
import persistent
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.content.text.interfaces
import zope.interface


@zope.interface.implementer(
    zeit.content.text.interfaces.IText,
    zeit.cms.interfaces.IAsset)
class Text(zeit.cms.repository.repository.ContentBase,
           persistent.Persistent):

    text = None

    zeit.cms.content.dav.mapProperties(
        zeit.content.text.interfaces.IText,
        zeit.content.text.interfaces.DAV_NAMESPACE,
        ('mimeType', 'encoding'),
        use_default=True)


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
        encoding = text.encoding  # Read from the DAV properties
        unicode_data = None
        if encoding:
            try:
                unicode_data = str(data, encoding)
            except UnicodeDecodeError:
                pass
        if unicode_data is None:
            # Guess encoding
            for encoding_term in (
                    zeit.content.text.interfaces.IText['encoding'].vocabulary):
                encoding = encoding_term.value
                try:
                    unicode_data = str(data, encoding)
                except UnicodeDecodeError:
                    pass
                else:
                    break
        assert unicode_data is not None
        if encoding != text.encoding:
            text.encoding = encoding
        text.text = unicode_data
        return text

    def resource_body(self, content):
        if isinstance(content.text, str):
            return BytesIO(content.text.encode(content.encoding))
        else:
            return BytesIO(content.text)

    def resource_content_type(self, content):
        return 'text/plain'
