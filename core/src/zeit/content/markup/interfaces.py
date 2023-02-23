from zeit.cms.i18n import MessageFactory as _

import zope.schema

import zeit.cms.content.interfaces


class IMarkup(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.content.interfaces.IXMLContent):

    text = zope.schema.Text(title=_('Insert markdown '))
