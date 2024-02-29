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

import filetype
import pytz
import zope.event

from zeit.connector.connector import CannonicalId
from zeit.connector.interfaces import ID_NAMESPACE, UUID_PROPERTY, CopyError, MoveError
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

    def __init__(self, repository_path, detect_mime_type=True):
        super().__init__(repository_path)
        self.detect_mime_type = detect_mime_type
        self._reset()

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product

        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        connector = super().factory()
        connector.detect_mime_type = config.get('detect-mime-type', True)
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

    def _get_content_type(self, id):
        result = super()._get_content_type(id)
        if result or not self.detect_mime_type:
            return result
        body = self._get_body(id)
        head = body.read(261)
        return filetype.guess_mime(head) or ''

    def __setitem__(self, id, object):
        resource = zeit.connector.interfaces.IResource(object)
        id = self._get_cannonical_id(id)
        iscoll = resource.type == 'collection' or resource.contentType == 'httpd/unix-directory'
        if iscoll and not id.endswith('/'):
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
        if resource.contentType == 'httpd/unix-directory':
            # XXX kludgy. We need to be able to differentiate directories,
            # so they get a trailing slash in their CanonicalId, but also
            # don't want to store random content types, so the filemagic
            # detetection e.g. for images takes over on the next read.
            properties[('getcontenttype', 'DAV:')] = resource.contentType
        properties[('getlastmodified', 'DAV:')] = str(
            datetime.datetime.now(pytz.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        )
        properties[('getetag', 'DAV:')] = repr(time.time()) + repr(random.random())

        self._set_properties(id, properties)

        zope.event.notify(zeit.connector.interfaces.ResourceInvaliatedEvent(id))

    def __delitem__(self, id):
        id = self._get_cannonical_id(id)
        self[id]  # may raise KeyError
        for _name, uid in self.listCollection(id):
            del self[uid]
        self._deleted.add(id)
        self._data.pop(id, None)
        self._properties.pop(id, None)
        zope.event.notify(zeit.connector.interfaces.ResourceInvaliatedEvent(id))

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
        self._ignore_uuid_checks = True
        r = self[old_id]
        r.id = new_id
        try:
            self.add(r, verify_etag=False)
        finally:
            self._ignore_uuid_checks = False
        if not new_id.endswith('/'):
            new_id = new_id + '/'
        for name, uid in self.listCollection(old_id):
            self.move(uid, urllib.parse.urljoin(new_id, name))
        del self[old_id]

    def _prevent_overwrite(self, old_id, new_id, exception):
        if zeit.connector.connector.Connector._is_descendant(new_id, old_id):
            raise exception(old_id, 'Could not copy or move %s to a decendant of itself.' % old_id)

        if new_id in self:
            # The target already exists. It's possible that there was a
            # conflict. Verify body.
            if (
                'httpd/unix-directory' in (self[old_id].contentType, self[new_id].contentType)
                or self[old_id].data.read() != self[new_id].data.read()
            ):
                raise exception(
                    old_id,
                    'Could not move %s to %s, because target alread exists.' % (old_id, new_id),
                )

    def changeProperties(self, id, properties):
        id = self._get_cannonical_id(id)
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        id = self._get_cannonical_id(id)
        self._locked[id] = (principal, until, True)

    def unlock(self, id, locktoken=None):
        id = self._get_cannonical_id(id)
        del self._locked[id]
        return locktoken

    def locked(self, id):
        id = self._get_cannonical_id(id)
        return self._locked.get(id, (None, None, False))

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
        if properties is not None:
            return properties
        properties = super()._get_properties(id)
        self._properties[id] = properties
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


class TextPlain(filetype.Type):
    """The `filetype` library only detects binary types.
    For some tests it is helpful to use a text type, because they can
    manipulate the contents more easily than in binary, so we cheat a little.
    """

    prefix = b'Mary had'

    def match(self, buf):
        return buf[: len(self.prefix)] == self.prefix


filetype.TYPES.append(TextPlain('text/plain', '.txt'))
