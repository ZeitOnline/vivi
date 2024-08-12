from io import BytesIO
import datetime
import http.client
import logging
import os
import os.path
import random
import time
import urllib.parse
import uuid

import pytz
import zope.event

from zeit.connector.connector import CannonicalId
from zeit.connector.interfaces import (
    ID_NAMESPACE,
    UUID_PROPERTY,
    CopyError,
    LockedByOtherSystemError,
    LockingError,
    MoveError,
)
from zeit.connector.lock import lock_is_foreign
import zeit.cms.config
import zeit.connector.cache
import zeit.connector.dav.interfaces
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
    canonical_id_cache = zeit.connector.cache.AlwaysEmptyDict()

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

        return connector

    def _reset(self):
        self._locked = {}
        self._data = {}
        self._paths = {}
        self._deleted = set()
        self._properties = {}
        self.search_result = self.search_result_default[:]

    def listCollection(self, id):
        """List the filenames of a collection identified by path."""
        return (
            (name, _id)
            for name, _id in super().listCollection(id)
            if _id not in self._deleted and _id + '/' not in self._deleted
        )

    def _get_collection_names(self, path):
        names = super()._get_collection_names(path)
        names |= self._paths.get(path, set())
        return names

    def getResourceType(self, id):
        id = self._get_cannonical_id(id)
        if id in self._deleted:
            raise KeyError("The resource '%s' does not exist." % id)
        return super().getResourceType(id)

    def __getitem__(self, id):
        id = self._get_cannonical_id(id)
        if id in self._deleted:
            raise KeyError(str(id))
        return super().__getitem__(id)

    def __setitem__(self, id, object):
        resource = zeit.connector.interfaces.IResource(object)
        id = self._get_cannonical_id(id)
        (principal, _, mylock) = self.locked(id)
        if principal and not mylock:
            raise LockedByOtherSystemError(id, '')
        if resource.is_collection and not id.endswith('/'):
            id = CannonicalId(id + '/')
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
                raise zeit.connector.dav.interfaces.PreconditionFailedError()

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
                if key == self._get_cannonical_id(resource.id):
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
            datetime.datetime.now(pytz.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        )
        properties[('getetag', 'DAV:')] = repr(time.time()) + repr(random.random())

        self._set_properties(id, properties)

        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(id))

    def __delitem__(self, id):
        id = self._get_cannonical_id(id)
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

    def _prevent_overwrite(self, old_id, new_id, exception):
        if zeit.connector.connector.Connector._is_descendant(new_id, old_id):
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
        id = self._get_cannonical_id(id)
        (principal, _, mylock) = self.locked(id)
        if principal and not mylock:
            raise LockedByOtherSystemError(id, '')
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        if id not in self:
            raise KeyError(f'The resource {id} does not exist')

        id = self._get_cannonical_id(id)
        (another_principal, _, my_lock) = self.locked(id)
        if another_principal:
            raise LockingError('Resource is already locked by another principal')
        self._locked[id] = (principal, until, my_lock)

    def unlock(self, id):
        id = self._get_cannonical_id(id)
        del self._locked[id]

    def _unlock(self, id, locktoken):
        self.unlock(id)

    def locked(self, id):
        if self.ignore_locking:
            return (None, None, False)
        id = self._get_cannonical_id(id)
        (lock_principal, until, my_lock) = self._locked.get(id, (None, None, False))
        if until and until < datetime.datetime.now(pytz.UTC):
            del self._locked[id]
            return (None, None, False)
        if lock_principal:
            my_lock = not lock_is_foreign(lock_principal)
        return (lock_principal, until, my_lock)

    search_result_default = [
        'http://xml.zeit.de/online/2007/01/Somalia',
        'http://xml.zeit.de/online/2007/01/Saarland',
        'http://xml.zeit.de/2006/52/Stimmts',
    ]

    def search(self, attributes, expression):
        log.debug('Searching: %s', expression._render())

        unique_ids = self.search_result

        metadata = ('pm', '07') + len(attributes) * (None,)
        metadata = metadata[: len(attributes)]

        return ((unique_id,) + metadata for unique_id in unique_ids)

    # internal helpers

    def _get_cannonical_id(self, id):
        """Add / for collections if not appended yet."""
        if isinstance(id, CannonicalId):
            return id
        if id == ID_NAMESPACE:
            return CannonicalId(id)
        if id.endswith('/'):
            id = id[:-1]
        if self._properties.get(id + '/') is not None:
            return CannonicalId(id + '/')
        if self._properties.get(id) is not None:
            return CannonicalId(id)
        path = self._path(id)
        if os.path.isdir(path):
            return CannonicalId(id + '/')
        return CannonicalId(id)

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
            elif not isinstance(value, str):  # XXX mimic DAV behaviour
                raise ValueError('Expected str, got %s: %r' % (type(value), value))
            else:
                stored_properties[(name, namespace)] = value
        self._properties[id] = stored_properties


factory = Connector.factory
