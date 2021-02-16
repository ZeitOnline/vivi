from os import environ, stat
from zope.component import getUtility
from zeit.connector.interfaces import IConnector


class ContentCache(object):

    def __getattr__(self, name):
        assert name == 'cache'
        size = environ.get('CONTENT_CACHE_SIZE')
        connector = getUtility(IConnector)
        if size is not None and hasattr(connector, '_path'):
            self.size = size
            self.connector = connector
            self.cache = {}
            return self.cache
        else:
            return None

    def path(self, unique_id):
        return self.connector._absolute_path(self.connector._path(unique_id))

    def mtime(self, filename):
        try:
            mtime = stat(filename).st_mtime
        except OSError:
            return None
        return int(mtime)

    def get(self, unique_id, key, factory, suffix=''):
        cache = self.cache
        if not unique_id or cache is None:
            return factory()
        obj = self.cache.setdefault(unique_id, {})
        if 'path' not in obj:
            obj['path'] = self.path(unique_id)
        mtime = self.mtime(obj['path'] + suffix)
        cache = obj.setdefault(mtime, {})
        if key not in cache:
            cache[key] = factory()
        return cache[key]


get = ContentCache().get
