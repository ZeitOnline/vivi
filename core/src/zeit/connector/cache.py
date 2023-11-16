from functools import total_ordering
from gocept.cache.method import Memoize as memoize
from io import BytesIO
from zope.dottedname.resolve import resolve
import BTrees
import ZODB.POSException
import ZODB.blob
import argparse
import collections.abc
import gocept.lxml.objectify
import logging
import lxml.objectify
import os
import persistent
import persistent.mapping
import tempfile
import time
import transaction
import urllib.request
import zc.set
import zeit.cms.cli
import zeit.connector.interfaces
import zope.interface
import zope.security.proxy


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


INVALID_ETAG = object()


class Body(persistent.Persistent):
    __slots__ = ('data', 'etag')

    def __init__(self):
        self.data = self.etag = None

    @property
    def BUFFER_SIZE(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        return int(config.get('body-cache-blob-threshold', 10 * 1024))

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

    def update(self, data, etag):
        if etag == self.etag:
            return
        self.etag = etag

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
        if commited[1]['etag'] == newstate[1]['etag']:
            return commited
        # Different ETags. Invalidate the cache.
        commited[1]['etag'] = INVALID_ETAG
        return commited


class AccessTimes:
    UPDATE_INTERVAL = NotImplemented

    def __init__(self):
        self._last_access_time = BTrees.family64.OI.BTree()
        self._access_time_to_ids = BTrees.family32.IO.BTree()

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
            new_set = self._access_time_to_ids[new_access_time] = BTrees.family32.OI.TreeSet()

        if old_set != new_set:
            if old_set is not None:
                try:
                    old_set.remove(key)
                except KeyError:
                    pass

            new_set.insert(key)
            self._last_access_time[key] = new_access_time

    def sweep(self, cache_timeout=(7 * 24 * 3600)):
        start = 0
        timeout = self._get_time_key(time.time() - cache_timeout)
        while True:
            try:
                access_time = next(iter(self._access_time_to_ids.keys(min=start, max=timeout)))
                id_set = []
                # For reasons unknown we sometimes get "the bucket being
                # iterated changed size" here, which according to
                # http://mail.zope.org/pipermail/zodb-dev/2004-June/007452.html
                # "can never happen". So we try to sweep all the IDs we can and
                # leave the rest to rot, rather than get stuck on one broken
                # access_time bucket and not be able to sweep anything after it
                try:
                    for id in self._access_time_to_ids[access_time]:
                        id_set.append(id)
                except RuntimeError:
                    pass
                try:
                    i = 0
                    retries = 0
                    while i < len(id_set):
                        id = id_set[i]
                        i += 1
                        log.info('Evicting %s', id)
                        self._last_access_time.pop(id, None)
                        try:
                            self.remove(id)
                        except KeyError:
                            pass  # already gone
                        if i % 100 == 0:
                            try:
                                log.info('Sub-commit')
                                transaction.commit()
                            except ZODB.POSException.ConflictError:
                                if retries == 3:
                                    raise RuntimeError('Too many retries')
                                log.info('ConflictError, retrying')
                                transaction.abort()
                                retries += 1
                                i -= 100
                    self._access_time_to_ids.pop(access_time, None)
                    start = access_time
                except Exception:
                    start = access_time + 1
                    log.info('Abort %s', access_time, exc_info=True)
                    transaction.abort()
                else:
                    log.info('Commit %s', access_time)
                    transaction.commit()
            except StopIteration:
                break

    def _get_time_key(self, time):
        return int(time / self.UPDATE_INTERVAL)


@zope.interface.implementer(zeit.connector.interfaces.IResourceCache)
class ResourceCache(AccessTimes, persistent.Persistent):
    """Cache for ressource data."""

    UPDATE_INTERVAL = 24 * 3600

    def __init__(self):
        super().__init__()
        self._data = BTrees.family64.OO.BTree()

    def getData(self, unique_id, properties):
        key = get_storage_key(unique_id)
        current_etag = properties[('getetag', 'DAV:')]

        value = self._data.get(key)
        if value is not None and not isinstance(value, Body):
            if isinstance(value, str):
                log.warning('Loaded str for %s' % unique_id)
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
            raise KeyError('Object %r is not cached.' % unique_id)
        self._update_cache_access(key)
        return value.open()

    def setData(self, unique_id, properties, data):
        key = get_storage_key(unique_id)
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            f = BytesIO(data.read())
            return f

        log.debug('Storing body of %s with etag %s' % (unique_id, current_etag))

        # Reuse previously stored container
        store = self._data.get(key)
        if store is None or not isinstance(store, Body):
            self._data[key] = store = Body()
        store.update(data, current_etag)

        self._update_cache_access(key)
        return store.open()

    def remove(self, unique_id):
        key = get_storage_key(unique_id)
        self._data.pop(key, None)


@zope.interface.implementer(zeit.connector.interfaces.IPersistentCache)
class PersistentCache(AccessTimes, persistent.Persistent):
    CACHE_VALUE_CLASS = None  # Set in subclass

    def __init__(self):
        super().__init__()
        self._storage = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        skey = get_storage_key(key)
        try:
            value = self._storage[skey]
        except KeyError:
            raise KeyError(key)
        if self._is_deleted(value):
            log.info('%s not found in %s', key, self)
            raise KeyError(key)
        self._update_cache_access(skey)
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        key = get_storage_key(key)
        value = self._storage.get(key, self)
        self._update_cache_access(key)
        return value is not self and not self._is_deleted(value)

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
        value = self._storage[get_storage_key(key)]
        if isinstance(value, self.CACHE_VALUE_CLASS):
            self._mark_deleted(value)
        else:
            self.remove(key)

    def remove(self, key):
        del self._storage[get_storage_key(key)]

    def __setitem__(self, key, value):
        skey = get_storage_key(key)
        old_value = self._storage.get(skey)
        if isinstance(old_value, self.CACHE_VALUE_CLASS):
            self._set_value(old_value, value)
        else:
            value = self.CACHE_VALUE_CLASS(value)
            self._storage[skey] = value
        self._update_cache_access(skey)

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

    # NOTE: By default, conflict resolution is performed by the ZEO *server*!
    def _p_resolveConflict(self, old, commited, newstate):
        if not FEATURE_TOGGLES.find('dav_cache_delete_property_on_conflict'):
            log.info('Overwriting %s with %s after ConflictError', commited, newstate)
            return newstate

        if not (list(old.keys()) == list(commited.keys()) == list(newstate.keys()) == ['data']):
            # We can only resolve data.
            raise ZODB.POSException.ConflictError
        commited_data = commited['data']
        newstate_data = newstate['data'].copy()

        commited_data.pop(('cached-time', 'INTERNAL'), None)
        newstate_data.pop(('cached-time', 'INTERNAL'), None)
        if newstate_data == commited_data:
            return newstate
        # Completely invalidate cache entry when we cannot resolve.
        log.info('Emptying %s due to ConflictError', newstate)
        old['data'] = {zeit.connector.interfaces.DeleteProperty: None}
        return old

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
    """Property cache."""

    CACHE_VALUE_CLASS = Properties

    UPDATE_INTERVAL = 24 * 3600

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
        if not FEATURE_TOGGLES.find('dav_cache_delete_childname_on_conflict'):
            raise ZODB.POSException.ConflictError()
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
    """Cache for child names."""

    CACHE_VALUE_CLASS = ChildNames
    UPDATE_INTERVAL = 24 * 3600

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


# Copy&paste from zeit.cms.content.sources to make it work in a ZEO environment
# where we have no dogpile setup, no product config, etc.pp.
class FeatureToggles:
    config_url = 'ZEIT_VIVI_FEATURE_TOGGLE_SOURCE'

    def find(self, name):
        try:
            return bool(getattr(self._get_tree(), name, False))
        except TypeError:
            return False

    def set(self, *names, **kw):  # only for tests
        for name in names:
            # Changes are discarded between tests by gocept.cache
            setattr(self._get_tree(), name, kw['value'])

    @memoize(300, ignore_self=True)
    def _get_tree(self):
        if self.config_url not in os.environ:
            return lxml.objectify.XML('<empty/>')
        return self._get_tree_from_url(os.environ[self.config_url])

    def _get_tree_from_url(self, url):
        __traceback_info__ = (url,)
        log.debug('Getting %s' % url)
        response = urllib.request.urlopen(url)
        return gocept.lxml.objectify.fromfile(response)


FEATURE_TOGGLES = FeatureToggles()


@zeit.cms.cli.runner()
def sweep():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=14)
    parser.add_argument('cache')
    options = parser.parse_args()
    iface = resolve('zeit.connector.interfaces.' + options.cache)
    cache = zope.component.getUtility(iface)
    cache.sweep(options.days * 24 * 3600)
    log.info('Sweep end')
