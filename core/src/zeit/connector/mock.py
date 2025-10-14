from io import BytesIO
import http.client
import logging
import os
import os.path
import random
import time
import urllib.parse
import uuid

from sqlalchemy.dialects import postgresql
import pendulum
import zope.event

from zeit.connector.interfaces import (
    ID_NAMESPACE,
    UUID_PROPERTY,
    CopyError,
    LockedByOtherSystemError,
    MoveError,
)
from zeit.connector.lock import lock_is_foreign
from zeit.connector.postgresql import Connector as SQLConnector
import zeit.cms.config
import zeit.cms.repository.interfaces
import zeit.connector.cache
import zeit.connector.filesystem
import zeit.connector.interfaces


log = logging.getLogger(__name__)


class Connector(zeit.connector.filesystem.Connector):
    """Connect to the CMS backend.

    The current implementation does *not* talk to the CMS backend but to
    some directory containing test content.

    """

    _ignore_uuid_checks = False
    _set_lastmodified_property = True
    resource_class = zeit.connector.resource.WriteableCachedResource

    property_cache = zeit.connector.cache.AlwaysEmptyDict()
    body_cache = zeit.connector.cache.AlwaysEmptyDict()
    child_name_cache = zeit.connector.cache.AlwaysEmptyDict()

    def __init__(self, repository_path, detect_mime_type=True, ignore_locking=False):
        super().__init__(repository_path)
        self.detect_mime_type = detect_mime_type
        self.ignore_locking = ignore_locking  # switch off lock validation, only for zeit.web tests
        self._reset()

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        config = zeit.cms.config.package('zeit.connector')
        connector = super().factory()
        connector.detect_mime_type = config.get('detect-mime-type', True)
        connector.ignore_locking = config.get('ignore-locking', False)
        if config.get('use-readonly-resource'):
            connector.resource_class = zeit.connector.resource.CachedResource

        return connector

    def _reset(self):
        self._locked = {}
        self._data = {}
        self._paths = {}
        self._deleted = set()
        self._properties = {}
        self.search_result = []
        self.search_result_count = None
        self.search_args = []
        self.search_dav_args = []

    def listCollection(self, id):
        """List the filenames of a collection identified by path."""
        id = SQLConnector._normalize(id)
        return ((name, _id) for name, _id in super().listCollection(id) if _id not in self._deleted)

    def _get_collection_names(self, path):
        names = super()._get_collection_names(path)
        names |= self._paths.get(path, set())
        return names

    def __getitem__(self, id):
        id = SQLConnector._normalize(id)
        if id in self._deleted:
            raise KeyError(str(id))
        return super().__getitem__(id)

    def __setitem__(self, id, object):
        resource = zeit.connector.interfaces.IResource(object)
        id = SQLConnector._normalize(id)
        (principal, _, mylock) = self.locked(id)
        if principal and not mylock:
            raise LockedByOtherSystemError(id, '')
        resource.id = str(id)  # override

        if id.rstrip('/') == ID_NAMESPACE.rstrip('/'):
            raise KeyError('Cannot write to root object')

        if id in self:
            old_etag = self[id].properties.get(('getetag', 'DAV:'))
        else:
            old_etag = None
        new_etag = resource.properties.get(('getetag', 'DAV:'))
        if new_etag and new_etag != old_etag:
            if id not in self or resource.data.read() != self[id].data.read():
                raise zeit.cms.repository.interfaces.ConflictError(resource.id)

        if id in self._deleted:
            self._deleted.remove(id)

        properties = dict(resource.properties)
        if not self._ignore_uuid_checks:
            existing_uuid = id in self and self[id].properties.get(UUID_PROPERTY)
            new_uuid = properties.get(UUID_PROPERTY)
            if not new_uuid:
                if existing_uuid:
                    new_uuid = existing_uuid
                else:
                    new_uuid = '{urn:uuid:%s}' % uuid.uuid4()
                properties[UUID_PROPERTY] = new_uuid
            else:
                if existing_uuid and existing_uuid != new_uuid:
                    raise http.client.HTTPException(409, 'Conflict')

            for key in self._properties.keys():
                if key == resource.id:
                    continue
                existing_uuid = self._properties[key].get(UUID_PROPERTY)
                if existing_uuid and existing_uuid == properties[UUID_PROPERTY]:
                    raise http.client.HTTPException(409, 'Conflict')

        # Just a very basic in-memory data storage for testing purposes.
        resource.data.seek(0)
        self._data[id] = resource.data.read()
        resource.data.close()
        path = self._path(id)
        self._paths.setdefault(os.path.dirname(path), set()).add(os.path.basename(path))

        properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = resource.type
        if resource.is_collection:
            properties[('getcontenttype', 'DAV:')] = 'httpd/unix-directory'
        properties[('getlastmodified', 'DAV:')] = str(
            pendulum.now('UTC').strftime('%a, %d %b %Y %H:%M:%S GMT')
        )
        properties[('getetag', 'DAV:')] = repr(time.time()) + repr(random.random())

        self._set_properties(id, properties)

        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(id))

    def __delitem__(self, id):
        id = SQLConnector._normalize(id)
        self[id]  # may raise KeyError
        (principal, _, mylock) = self.locked(id)
        if principal and not mylock:
            raise LockedByOtherSystemError(id, '')
        list_collection = self.listCollection(id)
        for _name, uid in list_collection:
            (principal, _, mylock) = self.locked(uid)
            if principal and not mylock:
                raise LockedByOtherSystemError(uid, '')
            del self[uid]
        self._deleted.add(id)
        self._data.pop(id, None)
        self._properties.pop(id, None)
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(id))

    def add(self, object, verify_etag=True):
        resource = zeit.connector.interfaces.IResource(object)
        if not verify_etag:
            resource.properties.pop(('getetag', 'DAV:'), None)
        self[resource.id] = resource

    def copy(self, old_id, new_id):
        old_id = SQLConnector._normalize(old_id)
        new_id = SQLConnector._normalize(new_id)
        self._prevent_overwrite(old_id, new_id, CopyError)
        r = self[old_id]
        r.id = new_id
        r.properties.pop(UUID_PROPERTY, None)
        self.add(r, verify_etag=False)
        if not new_id.endswith('/'):
            new_id = new_id + '/'
        for name, uid in self.listCollection(old_id):
            self.copy(uid, urllib.parse.urljoin(new_id, name))

    def move(self, old_id, new_id):
        old_id = SQLConnector._normalize(old_id)
        new_id = SQLConnector._normalize(new_id)
        self._prevent_overwrite(old_id, new_id, MoveError)
        (principal, _, mylock) = self.locked(old_id)
        if principal and not mylock:
            raise LockedByOtherSystemError(old_id, '')
        r = self[old_id]

        if new_id in self:
            raise MoveError(new_id, f'The resource {new_id} already exists.')
        r.id = new_id
        try:
            self._ignore_uuid_checks = True
            self.add(r, verify_etag=False)
        finally:
            self._ignore_uuid_checks = False
        if not new_id.endswith('/'):
            new_id = new_id + '/'
        for name, uid in self.listCollection(old_id):
            (principal, _, mylock) = self.locked(uid)
            if principal and not mylock:
                raise LockedByOtherSystemError(uid, '')
            self.move(uid, urllib.parse.urljoin(new_id, name))
        del self[old_id]

    @staticmethod
    def _is_descendant(id1, id2):
        """Return if id1 is descandant of id2.

        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b/c/d/e')
        False
        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b')
        True
        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b/d')
        False
        """
        path1 = urllib.parse.urlsplit(id1)[2].split('/')
        path2 = urllib.parse.urlsplit(id2)[2].split('/')
        return len(path2) <= len(path1) and path2 == path1[: len(path2)]

    def _prevent_overwrite(self, old_id, new_id, exception):
        if self._is_descendant(new_id, old_id):
            raise exception(old_id, 'Could not copy or move %s to a decendant of itself.' % old_id)

        if new_id in self:
            # The target already exists. It's possible that there was a
            # conflict. Verify body.
            if (
                self[old_id].is_collection
                or self[new_id].is_collection
                or self[old_id].data.read() != self[new_id].data.read()
            ):
                raise exception(
                    old_id,
                    'Could not move %s to %s, because target alread exists.' % (old_id, new_id),
                )

    def changeProperties(self, id, properties):
        id = SQLConnector._normalize(id)
        (principal, _, mylock) = self.locked(id)
        if principal and not mylock:
            raise LockedByOtherSystemError(id, '')
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        id = SQLConnector._normalize(id)
        if id not in self:
            raise KeyError(f'The resource {id} does not exist')

        id = SQLConnector._normalize(id)
        (another_principal, _, my_lock) = self.locked(id)
        if another_principal:
            raise LockedByOtherSystemError(id, '')
        self._locked[id] = (principal, until, my_lock)

    def unlock(self, id):
        id = SQLConnector._normalize(id)
        del self._locked[id]

    def _unlock(self, id, locktoken):
        id = SQLConnector._normalize(id)
        self.unlock(id)

    def locked(self, id):
        if self.ignore_locking:
            return (None, None, False)
        id = SQLConnector._normalize(id)
        (lock_principal, until, my_lock) = self._locked.get(id, (None, None, False))
        if until and until < pendulum.now('UTC'):
            del self._locked[id]
            return (None, None, False)
        if lock_principal:
            my_lock = not lock_is_foreign(lock_principal)
        return (lock_principal, until, my_lock)

    def search(self, attributes, expression, order=None, limit=None, offset=0):
        log.debug('Searching: %s', expression._render())
        self.search_dav_args.append((attributes, expression, order, limit, offset))
        result = []
        for item in self.search_result:
            if isinstance(item, str):
                item = (item,)
            missing = len(attributes) - len(item) - 1
            item += (None,) * missing
            result.append(item)
        return tuple(result)

    def _compile_sql(self, stmt):
        return str(
            stmt.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})
        )

    def search_sql(self, query, timeout=None, cache=True):
        self.search_args.append(self._compile_sql(query))
        for uniqueid in self.search_result:
            yield self[uniqueid]

    def search_sql_count(self, query):
        if self.search_result_count is not None:
            return self.search_result_count
        else:
            return len(list(self.search_sql(query)))

    def execute_sql(self, query, timeout=None):
        self.search_args.append(self._compile_sql(query))
        return self.search_result

    def update_references(self, uniqueid, references):
        pass  # will not be supported, use postgresql Connector instead.

    # internal helpers

    def _get_file(self, id):
        if id in self._data:
            value = self._data[id]
            if isinstance(value, str):
                value = value.encode('utf-8')
            return BytesIO(value)
        return super()._get_file(id)

    def _get_lastmodified(self, id):
        return 'Fri, 07 Mar 2008 12:47:16 GMT'

    def _get_properties(self, id):
        properties = self._properties.get(id)
        if properties is None:
            properties = super()._get_properties(id)
        else:
            properties = properties.copy()
        return properties

    def _set_properties(self, id, properties):
        stored_properties = self._get_properties(id)
        for (name, namespace), value in properties.items():
            if name.startswith('get') and name not in (
                'getlastmodified',
                'getetag',
                'getcontenttype',
            ):
                continue
            if value is zeit.connector.interfaces.DeleteProperty:
                stored_properties.pop((name, namespace), None)
                continue

            if not isinstance(value, str):
                raise ValueError('Expected str, got %s: %r' % (type(value), value))
            stored_properties[(name, namespace)] = value
        self._properties[id] = stored_properties


factory = Connector.factory
