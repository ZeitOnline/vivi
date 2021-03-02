import collections
import json
import logging
import re
import six
import zc.sourcefactory.basic
import zeit.cms.content.sources
import zope.interface
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE

log = logging.getLogger(__name__)


class AutomaticFeed(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, url, timeout):
        super(AutomaticFeed, self).__init__(id, title, None)
        self.url = url
        self.timeout = timeout


class AutomaticFeedSource(zeit.cms.content.sources.ObjectSource,
                          zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-automatic-feed-source'
    default_filename = 'cp-automatic-feeds.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            feed = AutomaticFeed(
                six.text_type(node.get('id')),
                six.text_type(node.text.strip()),
                six.text_type(node.get('url')),
                int(node.get('timeout', 2))
            )
            result[feed.id] = feed
        return result


AUTOMATIC_FEED_SOURCE = AutomaticFeedSource()


class TopicpageFilterSource(zc.sourcefactory.basic.BasicSourceFactory,
                            zeit.cms.content.sources.CachedXMLBase):

    COMMENT = re.compile(r'\s*//')

    product_configuration = 'zeit.content.cp'
    config_url = 'topicpage-filter-source'
    default_filename = 'topicpage-filters.json'

    def json_data(self):
        result = collections.OrderedDict()
        for row in self._get_tree():
            if len(row) != 1:
                continue
            key = list(row.keys())[0]
            result[key] = row[key]
        return result

    @CONFIG_CACHE.cache_on_arguments()
    def _get_tree_from_url(self, url):
        try:
            data = []
            for line in six.moves.urllib.request.urlopen(url):
                line = six.ensure_text(line)
                if self.COMMENT.search(line):
                    continue
                data.append(line)
            data = '\n'.join(data)
            return json.loads(data)
        except Exception:
            log.warning(
                'TopicpageFilterSource could not parse %s', url, exc_info=True)
            return {}

    def getValues(self):
        return self.json_data().keys()

    def getTitle(self, value):
        return self.json_data()[value].get('title', value)

    def getToken(self, value):
        return value


class IContentQuery(zope.interface.Interface):
    """Mechanism to retrieve content objects.
    Used to register named adapters for the different IArea.automatic_type's
    and article module ITopicbox.source_type's
    """

    total_hits = zope.interface.Attribute(
        'Total number of available results (only available after calling)')

    def __call__(self):
        """Returns list of content objects."""

    existing_teasers = zope.interface.Attribute(
        """Returns a set of ICMSContent objects that are already present on
        the CP in other areas and in topicboxes in articles.
        If IArea.hide_dupes is True, these should be not be repeated, and
        thus excluded from our query result.
        """)


class IConfiguration(zope.interface.Interface):
    referenced_topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage'),
        required=False)

    topicpage_filter = zope.schema.Choice(
        title=_('Topicpage filter'),
        source=TopicpageFilterSource(),
        required=False)

    rss_feed = zope.schema.Choice(
        title=_('RSS-Feed'),
        source=AUTOMATIC_FEED_SOURCE,
        required=False)
