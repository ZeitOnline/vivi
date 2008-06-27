# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import logging
import time

import persistent
import transaction
import BTrees
import ZODB.blob

import zope.component
import zope.interface
import zope.testing.cleanup

import zeit.connector.interfaces


logger = logging.getLogger(__name__)


def get_storage_key(key):
    if isinstance(key, unicode):
        key = key.encode('utf8')
    assert isinstance(key, str)
    return ''.join(reversed(key))


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)

    CACHE_TIMEOUT = 30 * 24 * 3600
    UPDATE_INTERVAL = 24 * 3600

    def __init__(self):
        self._etags = BTrees.family64.OO.BTree()
        self._data = BTrees.family64.OO.BTree()
        self._last_access_time = BTrees.family64.OI.BTree()
        self._time_to_id = BTrees.family64.IO.BTree()

    def getData(self, unique_id, properties):
        key = get_storage_key(unique_id)
        current_etag = properties[('getetag', 'DAV:')]
        cached_etag = self._etags.get(key)

        if current_etag != cached_etag:
            raise KeyError("Object %r is not cached." % unique_id)
        self._update_cache_access(key)
        return self._data[key].open('r')

    def setData(self, unique_id, properties, data):
        key = get_storage_key(unique_id)
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            f = StringIO.StringIO(data.read())
            return f

        logger.debug('Storing body of %s with etag %s' % (
            unique_id, current_etag))
        blob = ZODB.blob.Blob()
        blob_file = blob.open('w')
        buffer_size = 102400
        if hasattr(data, 'seek'):
            data.seek(0)
        s = data.read(buffer_size)
        while s:
            blob_file.write(s)
            s = data.read(buffer_size)
        blob_file.close()
        self._etags[key] = current_etag
        self._data[key] = blob
        self._update_cache_access(key)
        transaction.savepoint(optimistic=True)
        return blob.open('r')

    def _update_cache_access(self, key):
        last_access = self._last_access_time.get(key, 0)
        new_access = long(time.time() * 10e6)
        # only update if necessary
        if last_access + self.UPDATE_INTERVAL * 10e6 < new_access:
            logger.debug('Updating access time for %s' % key)
            self._last_access_time[key] = new_access

            if last_access:
                del self._time_to_id[last_access]
            self._time_to_id[new_access] = key

        self._sweep()

    def _sweep(self):
        timeout = long((time.time() - self.CACHE_TIMEOUT) * 10e6)
        for access_time in self._time_to_id.keys(max=timeout):
            key = self._time_to_id[access_time]
            del self._last_access_time[key]
            del self._time_to_id[access_time]
            del self._data[key]
            del self._etags[key]


class VolatileCache(persistent.Persistent):

    zope.interface.implements(zeit.connector.interfaces.IVolatileCache)

    _cache_valid = False

    def __init__(self):
        self._validate_cache()

    def __getitem__(self, key):
        self._validate_cache()
        try:
            return self._storage[get_storage_key(key)]
        except KeyError:
            raise KeyError(key)

    def get(self, key, default=None):
        self._validate_cache()
        return self._storage.get(get_storage_key(key), default)

    def __contains__(self, key):
        self._validate_cache()
        return get_storage_key(key) in self._storage

    def __delitem__(self, key):
        self._validate_cache()
        try:
            del self._storage[get_storage_key(key)]
        except KeyError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        self._validate_cache()
        self._storage[get_storage_key(key)] = value

    def _validate_cache(self):
        """Validate cache.

        The cache is invalidated when the server starts. The value
        `_cache_valid` is stored on the *class*, i.e. *not* in the database.
        When the server is started the cache is considered stale.

        """
        if not self._cache_valid:
            self._storage = BTrees.family32.OO.BTree()
            self.__class__._cache_valid = True


class PropertyCache(VolatileCache):
    """Property cache."""

    zope.interface.implements(zeit.connector.interfaces.IPropertyCache)
    _cache_valid = False


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_property_cache(event):
    cache = zope.component.getUtility(
        zeit.connector.interfaces.IPropertyCache)
    try:
        del cache[event.id]
    except KeyError:
        pass


class ChildNameCache(VolatileCache):
    """Cache for child names."""

    zope.interface.implements(zeit.connector.interfaces.IChildNameCache)
    _cache_valid = False


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_child_name_cache(event):
    cache = zope.component.getUtility(
        zeit.connector.interfaces.IChildNameCache)
    try:
        del cache[event.id]
    except KeyError:
        pass



# Test integration

def _cleanup():
    VolatileCache._cache_valid = False
    PropertyCache._cache_valid = False
    ChildNameCache._cache_valid = False

zope.testing.cleanup.addCleanUp(_cleanup)
