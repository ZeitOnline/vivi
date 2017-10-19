from zeit.cms.application import CONFIG_CACHE
import collections
import zeit.cms.content.sources
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


class JobTicker(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IJobTicker)

    source = NotImplemented

    @property
    def feed(self):
        # BBB jobbox_ticker_id was (needlessly) used on CPs from z.c.cp-3.14.0
        # up to z.c.modules-1.0
        source_id = self.xml.get('id') or self.xml.get('jobbox_ticker_id')
        if not source_id:
            source_id = 'default'
        res = self.source.factory.find(self, source_id)
        return res

    @feed.setter
    def feed(self, value):
        self.xml.set('id', value.id)


class Feed(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, available, teaser, landing_url, feed_url):
        super(Feed, self).__init__(id, title, available)
        self.id = id
        self.teaser = teaser
        self.landing_url = landing_url
        self.feed_url = feed_url


class FeedSource(zeit.cms.content.sources.ObjectSource,
                 zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'jobticker-source'

    def __init__(self, content_iface):
        self.content_iface = content_iface
        super(FeedSource, self).__init__()

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            feed = Feed(
                unicode(node.get('id')),
                unicode(node.get('title')),
                zeit.cms.content.sources.unicode_or_none(node.get(
                    'available')),
                unicode(node.get('teaser')),
                unicode(node.get('landing_url')),
                unicode(node.get('feed_url')))
            result[feed.id] = feed
        return result

    def isAvailable(self, value, context):
        content = self.content_iface(context, None)
        if not content:
            return False
        return super(FeedSource, self).isAvailable(value, content)
