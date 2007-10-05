# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import time

import persistent
import transaction
import BTrees.LOBTree
import BTrees.OLBTree
import BTrees.OOBTree
import ZODB.blob

import zope.annotation.factory
import zope.location.interfaces

import gocept.cache.property

import zeit.connector.interfaces


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)
    zope.component.adapts(zope.location.interfaces.ISite)

    properties = gocept.cache.property.TransactionBoundCache(
        '_v_properties', dict)
    child_ids = gocept.cache.property.TransactionBoundCache(
        '_v_childnames', dict)

    CACHE_TIMEOUT = 30 * 24 * 3600
    UPDATE_INTERVAL = 24 * 3600

    def __init__(self):
        self._etags = BTrees.OOBTree.OOBTree()
        self._data = BTrees.OOBTree.OOBTree()
        self._last_access_time = BTrees.OLBTree.OLBTree()
        self._time_to_id = BTrees.LOBTree.LOBTree()
        self.locktokens = BTrees.OOBTree.OOBTree()

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


resourceCacheFactory = zope.annotation.factory(ResourceCache)
