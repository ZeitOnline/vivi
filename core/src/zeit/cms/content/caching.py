from operator import itemgetter
from os import environ, stat
from zope.component import getUtility
from zeit.connector.interfaces import IConnector


class ContentCache(object):

    def __getattr__(self, name):
        if name != 'cache':
            raise AttributeError(name)
        size = environ.get('CONTENT_CACHE_SIZE')
        connector = getUtility(IConnector)
        if size is not None and hasattr(connector, '_path'):
            self.size = size
            self.connector = connector
            self.cache = {}
            self.hits = self.misses = 0
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
            self.misses += 1
        else:
            self.hits += 1
        obj['used'] = obj.get('used', 0) + 1
        return cache[key]

    @property
    def usage(self):
        cache = self.cache
        stats = (dict(uid=uid, used=cache[uid]['used']) for uid in cache)
        return sorted(stats, key=itemgetter('used'))

    def info(self):
        cache = self.cache
        usage = {info['uid']: info['used'] for info in reversed(self.usage)}
        return dict(
            size=self.size,
            count=len(cache),
            hits=self.hits,
            misses=self.misses,
            usage=usage)


__cache = ContentCache()
get = __cache.get
info = __cache.info
