# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import ZODB.POSException
import ZODB.blob
import cStringIO
import logging
import persistent
import persistent.mapping
import tempfile
import time
import zc.set
import zeit.connector.interfaces
import zope.interface
import zope.security.proxy
import zope.testing.cleanup


log = logging.getLogger(__name__)


def get_storage_key(key):
    if isinstance(key, unicode):
        key = key.encode('utf8')
    assert isinstance(key, str)
    return key


class StringRef(persistent.Persistent):
    # Legacy

    def __init__(self, s):
        self._str = s

    def open(self, mode):
        return cStringIO.StringIO(self._str)

    def update(self, new_data):
        self._str = new_data


class SlottedStringRef(StringRef):
    """A variant of StringRef using slots for less memory consumption."""
    # Legacy

    __slots__ = ('_str',)


INVALID_ETAG = object()


class Body(persistent.Persistent):

    BUFFER_SIZE = 10*1024
    __slots__ = ('data', 'etag')

    def __init__(self):
        self.data = self.etag = None

    def open(self, mode='r'):
        assert mode == 'r'
        if isinstance(self.data, ZODB.blob.Blob):
            try:
                commited_name = self.data.committed()
            except ZODB.blob.BlobError:
                # In the rather rare case that the blob was created in this
                # transaction, we have to copy the data to a temporary file.
                data = self.data.open('r')
                tmp = tempfile.NamedTemporaryFile(
                    prefix='zeit.connector.cache.')
                s = data.read(self.BUFFER_SIZE)
                while s:
                    tmp.write(s)
                    s = data.read(self.BUFFER_SIZE)
                tmp.seek(0, 0)
                data_file = open(tmp.name, 'rb')
            else:
                data_file = open(commited_name, 'rb')
        elif isinstance(self.data, str):
            data_file = cStringIO.StringIO(self.data)
        else:
            raise RuntimeError('self.data is of unsupported type %s' %
                               type(self.data))
        return data_file


    def update(self, data, etag):
        if etag == self.etag:
            return
        self.etag = etag

        if hasattr(data, 'seek'):
            data.seek(0)
        s = data.read(self.BUFFER_SIZE)
        if len(s) < self.BUFFER_SIZE:
            # Small object
            small = True
            target = cStringIO.StringIO()
        else:
            small = False
            self.data = ZODB.blob.Blob()
            target = self.data.open('w')
        while s:
            target.write(s)
            s = data.read(self.BUFFER_SIZE)

        if small:
            self.data = target.getvalue()
        else:
            target.close()

    def _p_resolveConflict(self, old, commited, newstate):
        if commited[1]['etag'] == newstate[1]['etag']:
            return commited
        # Different ETags. Invalidate the cache.
        commited[1]['etag'] = INVALID_ETAG
        return commited


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)

    CACHE_TIMEOUT = 30 * 24 * 3600
    UPDATE_INTERVAL = 24 * 3600

    def __init__(self):
        self._data = BTrees.family64.OO.BTree()
        self._last_access_time = BTrees.family64.OI.BTree()
        self._access_time_to_ids = BTrees.family32.IO.BTree()

    def getData(self, unique_id, properties):
        key = get_storage_key(unique_id)
        current_etag = properties[('getetag', 'DAV:')]

        value = self._data.get(key)
        if value is not None and not isinstance(value, Body):
            if isinstance(value, str):
                log.warning("Loaded str for %s" % unique_id)
                raise KeyError(unique_id)
            # Legacy, meke a temporary body
            old_etags = getattr(self, '_etags', None)
            etag = None
            if old_etags is not None:
                etag = old_etags.get(key)
            if etag is None:
                raise KeyError('No ETAG for legacy value.')
            body = Body()
            body.update(value.open('r'), etag)
            value = body

        if value is None or value.etag != current_etag:
            raise KeyError(u"Object %r is not cached." % unique_id)
        self._update_cache_access(key)
        return value.open()

    def setData(self, unique_id, properties, data):
        key = get_storage_key(unique_id)
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            f = cStringIO.StringIO(data.read())
            return f

        log.debug('Storing body of %s with etag %s' % (
            unique_id, current_etag))


        # Reuse previously stored container
        store = self._data.get(key)
        if store is None or not isinstance(store, Body):
            self._data[key] = store = Body()
        store.update(data, current_etag)

        self._update_cache_access(key)
        return store.open()

    def _update_cache_access(self, key):
        last_access_time = self._last_access_time.get(key, 0)
        new_access_time = self._get_time_key(time.time())

        old_set = None
        if last_access_time / 10e6 < 10e6:
            # Ignore old access times. This is to allow an update w/o downtime.
            old_set = self._access_time_to_ids.get(last_access_time)

        try:
            new_set = self._access_time_to_ids[new_access_time]
        except KeyError:
            new_set = self._access_time_to_ids[new_access_time] = (
                BTrees.family32.OI.TreeSet())

        if old_set != new_set:
            if old_set is not None:
                try:
                    old_set.remove(key)
                except KeyError:
                    pass

            new_set.insert(key)
            self._last_access_time[key] = new_access_time

    def sweep(self):
        timeout = self._get_time_key(time.time() - self.CACHE_TIMEOUT)
        access_times_to_remove = []
        for access_time in self._access_time_to_ids.keys(max=timeout):
            access_times_to_remove.append(access_time)
            id_set = self._access_time_to_ids[access_time]
            for id in id_set:
                self._last_access_time.pop(id, None)
                self._data.pop(id, None)
        for access_time in access_times_to_remove:
            self._access_time_to_ids.pop(access_time, None)

    def _get_time_key(self, time):
        return int(time / self.UPDATE_INTERVAL)


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
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        key = get_storage_key(key)
        value = self._storage.get(key, self)
        return value is not self and not self._is_deleted(value)

    def keys(self, include_deleted=False):
        keys = self._storage.keys()
        if include_deleted:
            return keys
        return (key for key in keys if key in self)

    def __delitem__(self, key):
        value = self._storage[get_storage_key(key)]
        if isinstance(value, self.CACHE_VALUE_CLASS):
            self._mark_deleted(value)
        else:
            self.remove(key)

    def remove(self, key):
        del self._storage[get_storage_key(key)]

    def __setitem__(self, key, value):
        old_value = self._storage.get(get_storage_key(key))
        if isinstance(old_value, self.CACHE_VALUE_CLASS):
            self._set_value(old_value, value)
        else:
            value = self.CACHE_VALUE_CLASS(value)
            self._storage[get_storage_key(key)] = value

    def _is_deleted(self, value):
        return zeit.connector.interfaces.DeleteProperty in value

    def _set_value(self, old_value, new_value):
        if self._cache_values_equal(old_value, new_value):
            return
        old_value.clear()
        old_value.update(new_value)


class WebDAVPropertyKey(object):

    __slots__ = ('name',)
    _instances = {}  # class variable

    def __new__(cls, name):
        instance = cls._instances.get(name)
        if instance is None:
            instance = cls._instances[name] = object.__new__(cls)
        return instance

    def __init__(self, name):
        assert not zope.security.proxy.isinstance(name, WebDAVPropertyKey)
        self.name = name

    def __getitem__(self, idx):
        return self.name.__getitem__(idx)

    def __cmp__(self, other):
        if zope.security.proxy.isinstance(other, WebDAVPropertyKey):
            return cmp(self.name, other.name)
        return cmp(self.name, other)

    def __hash__(self):
        assert not zope.security.proxy.isinstance(self.name, WebDAVPropertyKey)
        return hash(self.name)

    def __repr__(self):
        return '<WebDAVPropertyKey %s>' % (self.name,)

    def __reduce__(self):
        return (WebDAVPropertyKey, (self.name,))


zope.testing.cleanup.addCleanUp(WebDAVPropertyKey._instances.clear)


class Properties(persistent.mapping.PersistentMapping):

    cached_time = None

    def _p_resolveConflict(self, old, commited, newstate):
        if not (old.keys()
                == commited.keys()
                == newstate.keys()
                == ['data']):
            # We can only resolve data.
            raise ZODB.POSException.ConflictError
        commited_data = commited['data']
        newstate_data = newstate['data'].copy()

        commited_data.pop(('cached-time', 'INTERNAL'), None)
        newstate_data.pop(('cached-time', 'INTERNAL'), None)
        if newstate_data == commited_data:
            return newstate
        # Completely invalidate cache entry when we cannot resolve.
        old['data'] = {zeit.connector.interfaces.DeleteProperty: None}
        return old

    def __setitem__(self, key, value):
        key = zope.security.proxy.removeSecurityProxy(key)
        if (key is not zeit.connector.interfaces.DeleteProperty
            and not isinstance(key, WebDAVPropertyKey)):
            key = WebDAVPropertyKey(key)
        super(Properties, self).__setitem__(key, value)

    def update(self, dict=None, **kwargs):
        if dict is None:
            dict = {}
        for key, value in dict.items() + kwargs.items():
            self[key] = value
        self._p_changed = True

    def __repr__(self):
        return object.__repr__(self)


class PropertyCache(PersistentCache):
    """Property cache."""

    zope.interface.implements(zeit.connector.interfaces.IPropertyCache)

    CACHE_VALUE_CLASS = Properties

    def _mark_deleted(self, value):
        value.clear()
        value[zeit.connector.interfaces.DeleteProperty] = None

    @staticmethod
    def _cache_values_equal(a, b):
        return dict(a.items()) == dict(b.items())


class ChildNames(zc.set.Set):

    def _p_resolveConflict(self, old, commited, newstate):
        if commited == newstate:
            return commited
        old['_data'] = set([zeit.connector.interfaces.DeleteProperty])
        return old

    def __iter__(self):
        return iter(sorted(super(ChildNames, self).__iter__()))

    def __repr__(self):
        return object.__repr__(self)

    def insert(self, key):
        # BTree sets have insert instead of add. Let's be greedy.
        self.add(key)


class ChildNameCache(PersistentCache):
    """Cache for child names."""

    zope.interface.implements(zeit.connector.interfaces.IChildNameCache)

    CACHE_VALUE_CLASS = ChildNames

    def _mark_deleted(self, value):
        value.clear()
        value.add(zeit.connector.interfaces.DeleteProperty)

    @staticmethod
    def _cache_values_equal(a, b):
        return set(a) == set(b)
