# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import time

import persistent
import transaction
import BTrees.LOBTree
import BTrees.OLBTree
import BTrees.OOBTree
import ZODB.blob

import zope.component
import zope.interface
import zope.testing.cleanup

import zeit.connector.interfaces


logger = logging.getLogger(__name__)


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)

    CACHE_TIMEOUT = 30 * 24 * 3600
    UPDATE_INTERVAL = 24 * 3600

    def __init__(self):
        self._etags = BTrees.OOBTree.OOBTree()
        self._data = BTrees.OOBTree.OOBTree()
        self._last_access_time = BTrees.OLBTree.OLBTree()
        self._time_to_id = BTrees.LOBTree.LOBTree()

    def getData(self, unique_id, properties):
        current_etag = properties[('getetag', 'DAV:')]
        cached_etag = self._etags.get(unique_id)

        if current_etag != cached_etag:
            raise KeyError("Object %r is not cached." % unique_id)
        self._update_cache_access(unique_id)
        return self._data[unique_id].open('r')

    def setData(self, unique_id, properties, data):
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            return
        logger.debug('Storing body of %s with etag %s' % (
            unique_id, current_etag))
        blob = ZODB.blob.Blob()
        blob_file = blob.open('w')
        buffer_size = 102400
        if hasattr(data, 'seek'):
            data.seek(0)
        while True:
            s = data.read(buffer_size)
            blob_file.write(s)
            if len(s) < buffer_size:
                break
        blob_file.close()
        self._etags[unique_id] = current_etag
        self._data[unique_id] = blob
        self._update_cache_access(unique_id)
        transaction.savepoint(optimistic=True)
        return blob.open('r')

    def _update_cache_access(self, unique_id):
        last_access = self._last_access_time.get(unique_id, 0)
        new_access = long(time.time() * 10e6)
        # only update if necessary
        if last_access + self.UPDATE_INTERVAL * 10e6 < new_access:
            logger.debug('Updating access time for %s' % unique_id)
            self._last_access_time[unique_id] = new_access

            if last_access:
                del self._time_to_id[last_access]
            self._time_to_id[new_access] = unique_id

        self._sweep()

    def _sweep(self):
        timeout = long((time.time() - self.CACHE_TIMEOUT) * 10e6)
        for access_time in self._time_to_id.keys(max=timeout):
            unique_id = self._time_to_id[access_time]
            del self._last_access_time[unique_id]
            del self._time_to_id[access_time]


class VolatileCache(persistent.Persistent):

    zope.interface.implements(zeit.connector.interfaces.IVolatileCache)

    _cache_valid = False

    def __init__(self):
        self._validate_cache()

    def __getitem__(self, key):
        self._validate_cache()
        return self._storage[key]

    def get(self, key, default=None):
        self._validate_cache()
        return self._storage.get(key, default)

    def __contains__(self, key):
        self._validate_cache()
        return key in self._storage

    def __delitem__(self, key):
        self._validate_cache()
        del self._storage[key]

    def __setitem__(self, key, value):
        self._validate_cache()
        self._storage[key] = value

    def _validate_cache(self):
        """Validate cache.

        The cache is invalidated when the server starts. The value
        `_cache_valid` is stored on the *class*, i.e. *not* in the database.
        When the server is started the cache is considered stale.

        """
        if not self._cache_valid:
            self._storage = BTrees.OOBTree.OOBTree()
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
