import grokcore.component as grok
import lxml.etree
import zope.component

from zeit.cms.interfaces import CONFIG_CACHE
from zeit.retresco.connection import TOPIC_PAGE_ATTRIBUTES
import zeit.cms.content.sources
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.retresco.interfaces


@grok.implementer(zeit.cms.tagging.interfaces.IWhitelist)
class Whitelist(grok.GlobalUtility):
    """Search for known keywords using the Retresco API."""

    def search(self, term):
        return self._tms.get_keywords(term)

    def locations(self, term):
        return self._tms.get_locations(term)

    def get(self, id):
        return zeit.cms.tagging.tag.Tag.from_code(id)

    @property
    def _tms(self):
        return zope.component.getUtility(zeit.retresco.interfaces.ITMS)


@grok.implementer(zeit.cms.tagging.interfaces.ITopicpages)
class Topicpages(grok.GlobalUtility, zeit.cms.content.sources.OverridableURLConfiguration):
    product_configuration = 'zeit.retresco'
    config_url = 'topicpages-source'
    default_filename = 'topicpages.xml'

    def get_topics(self, start=0, rows=25, sort_by='title', sort_order='asc', firstletter=None):
        result = []
        tree = self.load()
        xpath = '//topic'
        if not firstletter:
            pass
        elif len(firstletter) == 1:
            xpath += f'[substring(@id, 1, 1) = "{firstletter.lower()}"]'
        else:
            xpath += f'[contains("{firstletter.lower()}", substring(@id, 1, 1))]'

        for node in tree.xpath(xpath):
            topic = {}
            for attr in TOPIC_PAGE_ATTRIBUTES:
                if len(attr) < 3:
                    name = attr[0]
                    typ = None
                elif len(attr) == 3:
                    name, _, typ = attr
                value = node.get(name)
                if value is None:
                    continue
                if typ is not None:
                    value = typ(value)
                topic[name] = value
            topic['title'] = node.text
            result.append(topic)

        rev = sort_order != 'asc'
        if sort_by == 'title':
            result.sort(key=lambda x: x.get(sort_by, '').lower(), reverse=rev)
        else:
            result.sort(key=lambda x: x.get(sort_by, -1), reverse=rev)

        hits = len(result)
        if rows is not None:
            result = result[start : start + rows]
        slice = zeit.cms.interfaces.Result(result)
        slice.hits = hits
        return slice

    @CONFIG_CACHE.cache_on_arguments()
    def load(self):  # Allow zeit.web to override the cache region
        return self._load()

    def _load(self):
        request = zeit.cms.content.sources.load(self.url)
        return lxml.etree.parse(request).getroot()
