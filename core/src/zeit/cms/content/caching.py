from collections import defaultdict
from logging import getLogger
from operator import itemgetter
from os import environ, stat
from os.path import join
from time import time
from zope.component import getUtility
from zeit.cms.interfaces import ID_NAMESPACE
from zeit.connector.interfaces import IConnector
from zeit.connector.filesystem import Connector


log = getLogger(__name__)


class ContentCache(object):

    def __getattr__(self, name):
        if name != 'cache':
            raise AttributeError(name)
        size = environ.get('CONTENT_CACHE_SIZE')
        check = environ.get('CONTENT_CACHE_CHECK')
        connector = getUtility(IConnector)
        if size is not None and type(connector) is Connector:
            self.size = int(size)
            self.check = int(check) if check is not None else self.size / 5
            self.connector = connector
            self.cache = defaultdict(dict)
            self.hits = self.misses = 0
            log.info('initialized content cache (size %s)', size)
            return self.cache
        else:
            return None

    def path(self, unique_id):
        if unique_id is not None and unique_id.startswith(ID_NAMESPACE):
            return unique_id.replace(ID_NAMESPACE, '', 1).rstrip('/')

    def mtime(self, path):
        filename = join(self.connector.repository_path, path)
        try:
            mtime = stat(filename).st_mtime
        except OSError:
            return None
        return int(mtime)

    def get(self, unique_id, key, factory, suffix=''):
        cache = self.cache
        path = self.path(unique_id)
        if not path or cache is None:
            return factory()
        mtime = self.mtime(path + suffix)
        if mtime is None:
            return factory()
        obj = cache[path]
        obj['used'] = obj.get('used', 0) + 1
        obj['last'] = time()
        if mtime != obj.setdefault('mtimes', {}).get(suffix):
            obj['data'] = {}
            obj['mtimes'][suffix] = mtime
        cache = obj['data']
        if key not in cache:
            cache[key] = factory()
            self.misses += 1
            log.debug('added %s (%s)', key, mtime)
            if self.misses % self.check == 0:
                self.cleanup()
        else:
            self.hits += 1
        return cache[key]

    def cleanup(self):
        cache = self.cache
        over = len(cache) - self.size
        log.info('size: %d/%d, hits: %d, misses: %d',
                 over + self.size, self.size, self.hits, self.misses)
        if over > 0:
            log.debug('removing %d items', over)
            last = sorted((cache[uid]['last'], uid) for uid in cache)
            for _, (_, uid) in zip(range(over), last):
                del cache[uid]

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
