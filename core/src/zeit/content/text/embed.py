from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


class Embed(zeit.content.text.text.Text):

    zope.interface.implements(zeit.content.text.interfaces.IEmbed)

    render_as_template = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IEmbed['render_as_template'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'render_as_template')


class EmbedType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IEmbed
    type = 'embed'
    title = _('Embed')
    factory = Embed
    addform = 'zeit.content.text.embed.Add'
