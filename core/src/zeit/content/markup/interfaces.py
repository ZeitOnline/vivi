from zeit.cms.i18n import MessageFactory as _

import zeit.cms.content.field
import zeit.cms.content.interfaces


class IMarkup(zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.content.interfaces.IXMLContent):
    text = zeit.cms.content.field.Markdown(title=_('Markdown content'), required=False)
