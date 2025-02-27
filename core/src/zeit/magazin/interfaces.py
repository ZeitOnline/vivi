import zc.form.field
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces
import zeit.content.portraitbox.interfaces


class IZMOSection(zeit.cms.section.interfaces.ISection):
    pass


class IZMOContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZMOFolder(
    zeit.cms.repository.interfaces.IFolder, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZMOArticle(
    zeit.content.article.interfaces.IArticle, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZMOCenterPage(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZMOPortraitbox(
    zeit.content.portraitbox.interfaces.IPortraitbox, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IPortraitboxLongtext(zope.interface.Interface):
    longtext = zc.form.field.HTMLSnippet(title=_('long text (ZMO)'), required=False)


class IHamburgSection(zeit.cms.section.interfaces.ISection):
    pass


class IHamburgContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


# BBB for existing content
class IZMOGallery(
    zeit.content.gallery.interfaces.IGallery, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZMOLink(zeit.content.link.interfaces.ILink, zeit.cms.section.interfaces.ISectionMarker):
    pass
