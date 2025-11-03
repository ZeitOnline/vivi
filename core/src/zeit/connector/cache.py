from functools import total_ordering
from io import BytesIO
import argparse
import collections.abc
import logging
import tempfile

from zope.dottedname.resolve import resolve
import BTrees
import opentelemetry.trace
import pendulum
import persistent
import persistent.mapping
import zc.set
import ZODB.blob
import ZODB.POSException
import zope.interface
import zope.security.proxy

import zeit.cms.cli
import zeit.cms.config
import zeit.connector.interfaces


log = logging.getLogger(__name__)


def get_storage_key(key):
    if isinstance(key, str):
        return key.encode('utf-8')
    return key


class StringRef(persistent.Persistent):
    # Legacy

    def __init__(self, s):
        self._str = s

    def open(self, mode):
        return BytesIO(self._str)

    def update(self, new_data):
        self._str = new_data


class SlottedStringRef(StringRef):
    """A variant of StringRef using slots for less memory consumption."""

    # Legacy

    __slots__ = ('_str',)


INVALID_ETAG = '__invalid__'


class Body(persistent.Persistent):
    __slots__ = ('data', 'etag')  # BBB remove etag field after refreshing zodb

    def __init__(self):
        self.data = self.etag = None

    @property
    def BUFFER_SIZE(self):
        return int(zeit.cms.config.get('zeit.connector', 'body-cache-blob-threshold', 10 * 1024))

    def open(self, mode='r'):
        assert mode == 'r'
        if isinstance(self.data, ZODB.blob.Blob):
            try:
                commited_name = self.data.committed()
            except ZODB.blob.BlobError:
                # In the rather rare case that the blob was created in this
                # transaction, we have to copy the data to a temporary file.
                data = self.data.open('r')
                tmp = tempfile.NamedTemporaryFile(prefix='zeit.connector.cache.')
                s = data.read(self.BUFFER_SIZE)
                while s:
                    tmp.write(s)
                    s = data.read(self.BUFFER_SIZE)
                data.close()
                tmp.seek(0, 0)
                data_file = open(tmp.name, 'rb')
            else:
                data_file = open(commited_name, 'rb')
        elif isinstance(self.data, str):
            data_file = BytesIO(self.data.encode('utf-8'))
        elif isinstance(self.data, bytes):
            data_file = BytesIO(self.data)
        else:
            raise RuntimeError('self.data is of unsupported type %s' % type(self.data))
        return data_file

    def update_data(self, data):
        if data.seekable():
            data.seek(0)
        s = data.read(self.BUFFER_SIZE)
        if len(s) < self.BUFFER_SIZE:
            # Small object
            small = True
            target = BytesIO()
        else:
            small = False
            self.data = ZODB.blob.Blob()
            target = self.data.open('w')
        while s:
            target.write(s)
            s = data.read(self.BUFFER_SIZE)
        data.close()

        if small:
            self.data = target.getvalue()
        target.close()

    def _p_resolveConflict(self, old, commited, newstate):
        log.info('Overwriting body after ConflictError')
        return newstate


class AccessTimes:
    """Stores most recent access time per cache key, with 'whole day' granularity,
    to support evicting cache entries that have not been accessed for a given time.
    """

    def __init__(self):
        # We're using the keys as an ordered set: every value is `1`, and the
        # key format is 'yyyymmdd_uniqueid', so we can efficiently retrieve
        # uniqueIds older than a given timestamp (for `sweep()`)
        self._sorted_access_time = BTrees.family64.OI.BTree()
        # Have to also store {uniqueid: timestamp}, so we can remove the previous
        # entry from _sorted_access_time efficiently.
        self._access_time_by_id = BTrees.family64.OI.BTree()

    def _update_cache_access(self, key):
        if not hasattr(self, '_sorted_access_time'):  # BBB
            AccessTimes.__init__(self)

        stored = self._access_time_by_id.get(key)
        new = self._get_time_key(pendulum.now())
        if stored == new:
            return
        self._access_time_by_id[key] = new
        key = key.decode('utf-8')
        self._sorted_access_time.pop(f'{stored}_{key}', None)
        self._sorted_access_time[f'{new}_{key}'] = 1

    def sweep(self, cache_timeout=7):
        # Make use of lexical sorting: `...x` is treated as greater than any
        # `...y_suffix` if x and y are digits and x>y
        timeout = str(self._get_time_key(pendulum.now().subtract(days=cache_timeout)))
        while True:
            batch = []
            for x in self._sorted_access_time.keys(max=timeout):
                if len(batch) == 100:
                    break
                batch.append(x)
            if not batch:
                break
            for _ in zeit.cms.cli.commit_with_retry():
                for item in batch:
                    _, _, key = item.partition('_')
                    log.info('Evicting %s', key)
                    self.pop(key, None)
                    self._access_time_by_id.pop(get_storage_key(key), None)
                    self._sorted_access_time.pop(item, None)

    def _get_time_key(self, timestamp):
        return timestamp.year * 10000 + timestamp.month * 100 + timestamp.day


@zope.interface.implementer(zeit.connector.interfaces.IResourceCache)
class ResourceCache(AccessTimes, persistent.Persistent):
    def __init__(self):
        super().__init__()
        self._data = BTrees.family64.OO.BTree()

    def __getitem__(self, uniqueid):
        key = get_storage_key(uniqueid)
        try:
            value = self._data.get(key)
            if value is None:
                raise KeyError('Object %r is not cached.' % uniqueid)
            self._update_cache_access(key)
            return value.open()
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            raise KeyError(key)

    def get(self, uniqueid, default=None):
        try:
            return self[uniqueid]
        except KeyError:
            return default

    def __contains__(self, uniqueid):
        key = get_storage_key(uniqueid)
        try:
            result = key in self._data
            if result:
                self._update_cache_access(key)
            return result
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            return False

    def update(self, uniqueid, value):
        key = get_storage_key(uniqueid)
        stored = self._data.get(key)
        if not isinstance(stored, Body):
            self._data[key] = stored = Body()
        try:
            stored.update_data(value)
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            self._data[key] = stored = Body()
            stored.update_data(value)
        self._update_cache_access(key)
        return stored.open()

    def pop(self, unique_id, default=None):
        key = get_storage_key(unique_id)
        return self._data.pop(key, default)

    remove = pop


@zope.interface.implementer(zeit.connector.interfaces.IPersistentCache)
class PersistentCache(AccessTimes, persistent.Persistent):
    CACHE_VALUE_CLASS = None  # Set in subclass

    def __init__(self):
        super().__init__()
        self._storage = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        skey = get_storage_key(key)
        try:
            try:
                value = self._storage[skey]
            except KeyError:
                raise KeyError(key)
            if self._is_deleted(value):
                log.info('%s not found in %s', key, self)
                raise KeyError(key)
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            raise KeyError(key)
        self._update_cache_access(skey)
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        try:
            key = get_storage_key(key)
            value = self._storage.get(key, self)
            if value is not self:
                self._update_cache_access(key)
            return value is not self and not self._is_deleted(value)
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            return False

    def keys(self, include_deleted=False, min=None, max=None):
        if min is not None:
            min = get_storage_key(min)
        if max is not None:
            max = get_storage_key(max)
        keys = self._storage.keys(min=min, max=max)
        if include_deleted:
            return keys
        return (key for key in keys if key in self)

    def __delitem__(self, key):
        try:
            value = self._storage[get_storage_key(key)]
            if isinstance(value, self.CACHE_VALUE_CLASS):
                self._mark_deleted(value)
            else:
                self.remove(key)
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            self.remove(key)

    def remove(self, key):
        del self._storage[get_storage_key(key)]

    def pop(self, key, default):
        return self._storage.pop(get_storage_key(key), default)

    def __setitem__(self, key, value):
        try:
            skey = get_storage_key(key)
            old_value = self._storage.get(skey)
            if isinstance(old_value, self.CACHE_VALUE_CLASS):
                self._set_value(old_value, value)
            else:
                value = self.CACHE_VALUE_CLASS(value)
                self._storage[skey] = value
            self._update_cache_access(skey)
        except ZODB.POSException.POSKeyError as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            self.remove(key)

    def _is_deleted(self, value):
        return zeit.connector.interfaces.DeleteProperty in value

    def _set_value(self, old_value, new_value):
        if self._cache_values_equal(old_value, new_value):
            return
        old_value.clear()
        old_value.update(new_value)


@total_ordering
class WebDAVPropertyKey:
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

    def __eq__(self, other):
        if zope.security.proxy.isinstance(other, WebDAVPropertyKey):
            return self.name == other.name
        return self.name == other

    def __lt__(self, other):
        if zope.security.proxy.isinstance(other, WebDAVPropertyKey):
            return self.name < other.name
        return self.name < other

    def __hash__(self):
        assert not zope.security.proxy.isinstance(self.name, WebDAVPropertyKey)
        return hash(self.name)

    def __repr__(self):
        return '<WebDAVPropertyKey %s>' % (self.name,)

    def __reduce__(self):
        return (WebDAVPropertyKey, (self.name,))


try:
    import zope.testing.cleanup

    zope.testing.cleanup.addCleanUp(WebDAVPropertyKey._instances.clear)
except ImportError:
    pass


class Properties(persistent.mapping.PersistentMapping):
    cached_time = None

    def _p_resolveConflict(self, old, commited, newstate):
        log.info('Overwriting %s with %s after ConflictError', commited, newstate)
        return newstate

    def __setitem__(self, key, value):
        key = zope.security.proxy.removeSecurityProxy(key)
        if key is not zeit.connector.interfaces.DeleteProperty and not isinstance(
            key, WebDAVPropertyKey
        ):
            key = WebDAVPropertyKey(key)
        super().__setitem__(key, value)

    def update(self, dict=None, **kwargs):
        if dict is None:
            dict = {}
        for key, value in list(dict.items()) + list(kwargs.items()):
            self[key] = value
        self._p_changed = True

    def __repr__(self):
        return object.__repr__(self)


@zope.interface.implementer(zeit.connector.interfaces.IPropertyCache)
class PropertyCache(PersistentCache):
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
        log.info('Emptying %s due to ConflictError', newstate)
        old['_data'] = {zeit.connector.interfaces.DeleteProperty}
        return old

    def __iter__(self):
        return iter(sorted(super().__iter__()))

    def __repr__(self):
        return object.__repr__(self)

    def insert(self, key):
        # BTree sets have insert instead of add. Let's be greedy.
        self.add(key)


@zope.interface.implementer(zeit.connector.interfaces.IChildNameCache)
class ChildNameCache(PersistentCache):
    CACHE_VALUE_CLASS = ChildNames

    def _mark_deleted(self, value):
        value.clear()
        value.add(zeit.connector.interfaces.DeleteProperty)

    @staticmethod
    def _cache_values_equal(a, b):
        return set(a) == set(b)


class AlwaysEmptyDict(collections.abc.MutableMapping):
    """Used by mock connector to disable filesystem transaction bound cache."""

    def __getitem__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def keys(self):
        return ()

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())


@zeit.cms.cli.runner()
def sweep():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=14)
    parser.add_argument('cache')
    options = parser.parse_args()
    iface = resolve('zeit.connector.interfaces.' + options.cache)
    cache = zope.component.getUtility(iface)
    for _ in zeit.cms.cli.commit_with_retry():
        cache.sweep(options.days)
    log.info('Sweep end')
