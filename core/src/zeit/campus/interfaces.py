import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.sources
import zeit.content.article.interfaces


class StudyCourse(zeit.cms.content.sources.AllowedBase):
    def __init__(self, id, title, available, text, href, button_text):
        super().__init__(id, title, available)
        self.text = text
        self.href = href
        self.button_text = button_text

    def is_allowed(self, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super().is_allowed(article)


class StudyCourseSource(zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.campus'
    config_url = 'article-stoa-source'
    default_filename = 'article-stoa.xml'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = {}
        for node in tree.iterchildren('*'):
            g = node.get
            id = node.get(self.attribute)
            result[id] = StudyCourse(
                id,
                g('vivi_title'),
                g('available', None),
                self._get_title_for(node),
                g('href', None),
                g('button_text', None),
            )
        return result


STUDY_COURSE_SOURCE = StudyCourseSource()


class IStudyCourse(zeit.edit.interfaces.IBlock):
    # For editing
    course = zope.schema.Choice(title=_('Study course'), required=True, source=STUDY_COURSE_SOURCE)
