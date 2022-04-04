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

    def get_topics(self, start=0, rows=25):
        result = []
        tree = self.load()
        for node in tree.iterchildren('*'):
            topic = {}
            for name in TOPIC_PAGE_ATTRIBUTES:
                topic[name] = node.get(name)
            result.append(topic)
        return result[start:start + rows]

    @CONFIG_CACHE.cache_on_arguments()
    def load(self):  # Allow zeit.web to override the cache region
        return self._load()

    def _load(self):
        request = urllib.request.urlopen(self.url)
        return gocept.lxml.objectify.fromfile(request)
