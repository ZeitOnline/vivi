import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.markup.interfaces


MARKUP_TEMPLATE = """\
<markup xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
</markup>
"""


@grok.implementer(zeit.content.markup.interfaces.IMarkup, zeit.cms.interfaces.IAsset)
class Markup(zeit.cms.content.metadata.CommonMetadata):
    default_template = MARKUP_TEMPLATE

    text = zeit.cms.content.property.Structure('.text')

    @property
    def teaserText(self):
        """for metadata preview, return text as teaser text
        to display it.
        If text is longer than 15 words, shorten it
        """
        if self.text and self.text.count(' ') > 15:
            teaser = ' '.join(self.text.split(' ')[:10])
            return f'{teaser} ...'
        return self.text


class MarkupType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Markup
    interface = zeit.content.markup.interfaces.IMarkup
    title = _('Markup content')
    type = 'markup'
