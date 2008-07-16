# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import cStringIO
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
    return key

class StringRef(persistent.Persistent):

    def __init__(self, s):
        self._str = s

    def open(self, mode):
        return cStringIO.StringIO(self._str)


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)

    CACHE_TIMEOUT = 30 * 24 * 3600
    UPDATE_INTERVAL = 24 * 3600
    BUFFER_SIZE = 10*1024

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
        value = self._data[key]
        if isinstance(value, str):
            logger.warning("Loaded str for %s" % unique_id)
            raise KeyError(unique_id)
        return self._make_filelike(value)

    def setData(self, unique_id, properties, data):
        key = get_storage_key(unique_id)
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            f = cStringIO.StringIO(data.read())
            return f

        logger.debug('Storing body of %s with etag %s' % (
            unique_id, current_etag))

        target = cStringIO.StringIO()

        if hasattr(data, 'seek'):
            data.seek(0)
        s = data.read(self.BUFFER_SIZE)
        if len(s) < self.BUFFER_SIZE:
            # Small object
            small = True
        else:
            small = False
            blob = ZODB.blob.Blob()
            blob_file = blob.open('w')
            target = blob_file

        while s:
            target.write(s)
            s = data.read(self.BUFFER_SIZE)

        if small:
            store = StringRef(target.getvalue())
        else:
            blob_file.close()
            store = blob

        self._etags[key] = current_etag
        self._data[key] = store
        self._update_cache_access(key)
        transaction.savepoint(optimistic=True)
        return self._make_filelike(store)

    def _make_filelike(self, blob_or_str):
        if isinstance(blob_or_str, str):
            # Legacy
            return cStringIO.StringIO(blob_or_str)
        return blob_or_str.open('r')

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


class PersistentCache(persistent.Persistent):

    zope.interface.implements(zeit.connector.interfaces.IPersistentCache)

    CACHE_VALUE_CLASS = None  # Set in subclass

    def __init__(self):
        self._storage = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        try:
            value = self._storage[get_storage_key(key)]
        except KeyError:
            raise KeyError(key)
        if self._is_deleted(value):
            raise KeyError(key)
        value = self._simplify(value)
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return get_storage_key(key) in self._storage

    def __delitem__(self, key):
        value = self._storage[get_storage_key(key)]
        if isinstance(value, self.CACHE_VALUE_CLASS):
            self._mark_deleted(value)
        else:
            del self._storage[get_storage_key(key)]

    def __setitem__(self, key, value):
        value = self._simplify(value)
        old_value = self._storage.get(get_storage_key(key))
        if isinstance(old_value, self.CACHE_VALUE_CLASS):
            self._set_value(old_value, value)
        else:
            value = self.CACHE_VALUE_CLASS(value)
            self._storage[get_storage_key(key)] = value

    def _is_deleted(self, value):
        return zeit.connector.interfaces.DeleteProperty in value

    def _set_value(self, old_value, new_value):
        old_value.clear()
        old_value.update(new_value)

    def _simplify(self, value):
        return value


class WebDAVPropertyKey(object):

    __slots__ = ('name',)
    _instances = {}  # class variable

    def __new__(cls, name):
        instance = cls._instances.get(name)
        if instance is None:
            instance = cls._instances[name] = object.__new__(cls)
        return instance

    def __init__(self, name):
        self.name = name

    def __getitem__(self, idx):
        return self.name.__getitem__(idx)

    def __cmp__(self, other):
        if isinstance(other, WebDAVPropertyKey):
            return cmp(self.name, other.name)
        return cmp(self.name, other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<WebDAVPropertyKey %s>' % (self.name,)

    def __reduce__(self):
        return (WebDAVPropertyKey, (self.name,))


zope.testing.cleanup.addCleanUp(WebDAVPropertyKey._instances.clear)


class PropertyCache(PersistentCache):
    """Property cache."""

    zope.interface.implements(zeit.connector.interfaces.IPropertyCache)

    CACHE_VALUE_CLASS = BTrees.family32.OO.BTree

    def _mark_deleted(self, value):
        value.clear()
        value[zeit.connector.interfaces.DeleteProperty] = None

    def _simplify(self, old_dict):
        new_dict = {}
        for key, value in old_dict.items():
            if not isinstance(key, WebDAVPropertyKey):
                key = WebDAVPropertyKey(key)
            new_dict[key] = value
        return new_dict


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_property_cache(event):
    cache = zope.component.getUtility(
        zeit.connector.interfaces.IPropertyCache)
    try:
        del cache[event.id]
    except KeyError:
        pass


class ChildNameCache(PersistentCache):
    """Cache for child names."""

    zope.interface.implements(zeit.connector.interfaces.IChildNameCache)

    CACHE_VALUE_CLASS = BTrees.family32.OO.TreeSet

    def _mark_deleted(self, value):
        value.clear()
        value.insert(zeit.connector.interfaces.DeleteProperty)


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_child_name_cache(event):
    cache = zope.component.getUtility(
        zeit.connector.interfaces.IChildNameCache)
    try:
        del cache[event.id]
    except KeyError:
        pass
