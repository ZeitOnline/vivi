import zope.interface

from zeit.cms.i18n import MessageFactory as _

import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces


class IZCOSection(zeit.cms.section.interfaces.ISection):
    pass


class IZCOContent(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZCOFolder(
        zeit.cms.repository.interfaces.IFolder,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZCOArticle(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZCOCenterPage(
        zeit.content.cp.interfaces.ICenterPage,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZCOGallery(
        zeit.content.gallery.interfaces.IGallery,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZCOLink(
        zeit.content.link.interfaces.ILink,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class ITopicpageLink(zope.interface.Interface):

    topicpage = zope.schema.Choice(
        title=_("Topicpage link"),
        required=False,
        source=zeit.content.cp.interfaces.centerPageSource)

    label = zope.schema.TextLine(
        title=_("Topicpagelink label"),
        required=False,
        constraint=zeit.cms.interfaces.valid_name)
