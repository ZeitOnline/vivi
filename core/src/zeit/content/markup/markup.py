from zeit.cms.i18n import MessageFactory as _

import grokcore.component as grok

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


@grok.implementer(
    zeit.content.markup.interfaces.IMarkup,
    zeit.cms.interfaces.IAsset)
class Markup(zeit.cms.content.metadata.CommonMetadata):

    default_template = MARKUP_TEMPLATE

    text = zeit.cms.content.property.Structure('.text')


class MarkupType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Markup
    interface = zeit.content.markup.interfaces.IMarkup
    title = _('Markup content')
    type = 'markup'
