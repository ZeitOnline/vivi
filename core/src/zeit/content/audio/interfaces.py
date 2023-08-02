from zeit.cms.i18n import MessageFactory as _
import zope.schema
import zeit.cms.content.interfaces


class IAudio(zeit.cms.content.interfaces.IXMLContent):
    title = zope.schema.TextLine(title=_("Title"))
