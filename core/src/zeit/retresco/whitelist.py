from zeit.cms.interfaces import CONFIG_CACHE
from zeit.retresco.connection import TOPIC_PAGE_ATTRIBUTES
import gocept.lxml.objectify
import grokcore.component as grok
import urllib.request
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.retresco.interfaces
import zope.component


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
class Topicpages(grok.GlobalUtility,
                 zeit.cms.content.sources.OverridableURLConfiguration):

    product_configuration = 'zeit.retresco'
    config_url = 'topicpages-source'
    default_filename = 'topicpages.xml'

    def get_topics(self, start=0, rows=25, sort_by='id', sort_order='asc',
                   firstletter=None):
        result = []
        tree = self.load()
        xpath = '//topic'
        if not firstletter:
            pass
        elif len(firstletter) == 1:
            xpath += f'[substring(@id, 1, 1) = "{firstletter.lower()}"]'
        else:
            xpath += (
                f'[contains("{firstletter.lower()}", substring(@id, 1, 1))]')

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
            result.append(topic)

        result.sort(key=lambda x: x.get(sort_by, -1),
                    reverse=(sort_order != 'asc'))
        slice = zeit.cms.interfaces.Result(result[start:start + rows])
        slice.hits = len(result)
        return slice

    @CONFIG_CACHE.cache_on_arguments()
    def load(self):  # Allow zeit.web to override the cache region
        return self._load()

    def _load(self):
        request = urllib.request.urlopen(self.url)
        return gocept.lxml.objectify.fromfile(request)
