from collections import defaultdict
from logging import getLogger
from operator import itemgetter
from os import environ
from time import time

from zope.cachedescriptors.property import Lazy as cachedproperty
from zope.component import getUtility

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.connector.filesystem import Connector
from zeit.connector.interfaces import IConnector


log = getLogger(__name__)


class ContentCache:
    @cachedproperty
    def cache(self):
        size = environ.get('CONTENT_CACHE_SIZE')
        check = environ.get('CONTENT_CACHE_CHECK')
        connector = getUtility(IConnector)
        if size is not None and type(connector) is Connector:
            self.size = int(size)
            self.check = int(check) if check is not None else self.size / 5
            self.connector = connector
            self.cache = defaultdict(lambda: {'used': 0, 'mtimes': {}, 'data': {}})
            self.hits = self.misses = 0
            log.info('initialized content cache (size %s)', size)
            return self.cache
        else:
            return None

    def get(self, unique_id, key, factory, suffix=''):
        cache = self.cache
        if cache is None or not FEATURE_TOGGLES.find('content_caching'):
            return factory()
        try:
            mtime = int(self.connector.mtime(unique_id, suffix))
        except (ValueError, TypeError):
            mtime = None
        if mtime is None:
            return factory()
        obj = cache[unique_id]
        obj['used'] += 1
        obj['last'] = time()
        if mtime != obj['mtimes'].get(suffix):
            obj['data'].clear()
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
        log.info(
            'size: %d/%d, hits: %d, misses: %d', over + self.size, self.size, self.hits, self.misses
        )
        if over > 0:
            log.debug('removing %d items', over)
            last = sorted((cache[uid]['last'], uid) for uid in cache)
            for _, (_, uid) in zip(range(over), last):
                del cache[uid]

    @property
    def usage(self):
        cache = self.cache
        stats = ({'uid': uid, 'used': cache[uid]['used']} for uid in cache)
        return sorted(stats, key=itemgetter('used'))

    def info(self):
        cache = self.cache
        usage = {info['uid']: info['used'] for info in reversed(self.usage)}
        return {
            'size': self.size,
            'count': len(cache),
            'hits': self.hits,
            'misses': self.misses,
            'usage': usage,
        }


__cache = ContentCache()
get = __cache.get
info = __cache.info
