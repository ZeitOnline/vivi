# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zope.schema


class IVolume(zeit.cms.content.interfaces.IXMLContent):

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)
