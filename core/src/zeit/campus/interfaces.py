from zeit.cms.interfaces import CONFIG_CACHE
from zeit.cms.i18n import MessageFactory as _
import collections
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.source
import zeit.content.gallery.interfaces
import zeit.content.infobox.interfaces
import zeit.content.link.interfaces
import zope.interface


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


class IZCOInfobox(
        zeit.content.infobox.interfaces.IInfobox,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class ITopic(zope.interface.Interface):

    page = zope.schema.Choice(
        title=_("Topic page"),
        required=False,
        source=zeit.content.cp.source.centerPageSource)

    label = zope.schema.TextLine(
        title=_("Topic label"),
        required=False)


class StudyCourse(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, available, text, href, button_text):
        super().__init__(id, title, available)
        self.text = text
        self.href = href
        self.button_text = button_text

    def is_allowed(self, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super().is_allowed(article)


class StudyCourseSource(
        zeit.cms.content.sources.ObjectSource,
        zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.campus'
    config_url = 'article-stoa-source'
    default_filename = 'article-stoa.xml'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            g = node.get
            id = node.get(self.attribute)
            result[id] = StudyCourse(
                id, g('vivi_title'), g('available', None),
                self._get_title_for(node), g('href', None),
                g('button_text', None))
        return result


STUDY_COURSE_SOURCE = StudyCourseSource()


class IStudyCourse(zeit.edit.interfaces.IBlock):

    # For editing
    course = zope.schema.Choice(
        title=_('Study course'),
        required=True,
        source=STUDY_COURSE_SOURCE)
