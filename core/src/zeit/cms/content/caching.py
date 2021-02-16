from os import environ
from zope.component import getUtility
from zeit.connector.interfaces import IConnector


class ContentCache(object):

    def __getattr__(self, name):
        assert name == 'cache'
        size = environ.get('CONTENT_CACHE_SIZE')
        connector = getUtility(IConnector)
        if size is not None and hasattr(connector, '_get_lastmodified'):
            self.size = size
            self.connector = connector
            self.cache = {}
            return self.cache
        else:
            return None

    def get(self, unique_id, key, factory):
        cache = self.cache
        if not unique_id or cache is None:
            return factory()
        mtime = self.connector._get_lastmodified(unique_id, raw=True)
        cache = self.cache.setdefault(unique_id, {}).setdefault(mtime, {})
        if key not in cache:
            cache[key] = factory()
        return cache[key]


get = ContentCache().get
