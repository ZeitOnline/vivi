# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.interfaces
import zope.interface
import zope.schema


class IZMOSection(zeit.cms.section.interfaces.ISection):
    pass


class IZMOContent(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZMOArticle(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IArticleTemplateSettings(zope.interface.Interface):

    template = zope.schema.TextLine(
        title=_("Template"),
        required=False)

    header_layout = zope.schema.TextLine(
        title=_("Header layout"),
        required=False)
