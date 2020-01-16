from io import BytesIO
from zeit.connector.connector import CannonicalId
from zeit.connector.interfaces import UUID_PROPERTY
import datetime
import logging
import os
import os.path
import pkg_resources
import pytz
import random
import six
import six.moves.http_client
import six.moves.urllib.parse
import time
import uuid
import zeit.connector.cache
import zeit.connector.dav.interfaces
import zeit.connector.filesystem
import zeit.connector.interfaces
import zope.event


ID_NAMESPACE = u'http://xml.zeit.de/'

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

    def __init__(self, repository_path):
        super(Connector, self).__init__(repository_path)
        self._reset()

    def _reset(self):
        self._locked = {}
        self._data = {}
        self._paths = {}
        self._deleted = set()
        self._properties = {}

    def listCollection(self, id):
        """List the filenames of a collection identified by path. """
        return (
            (name, _id)
            for name, _id in super(Connector, self).listCollection(id)
            if _id not in self._deleted and _id + u'/' not in self._deleted)

    def _get_collection_names(self, path):
        names = super(Connector, self)._get_collection_names(path)
        names |= self._paths.get(path, set())
        return names

    def getResourceType(self, id):
        id = self._get_cannonical_id(id)
        if id in self._deleted:
            raise KeyError("The resource '%s' does not exist." % id)
        return super(Connector, self).getResourceType(id)

    def __getitem__(self, id):
        id = self._get_cannonical_id(id)
        if id in self._deleted:
            raise KeyError(six.text_type(id))
        return super(Connector, self).__getitem__(id)

    def __setitem__(self, id, object):
        resource = zeit.connector.interfaces.IResource(object)
        id = self._get_cannonical_id(id)
        iscoll = (resource.type == 'collection' or
                  resource.contentType == 'httpd/unix-directory')
        if iscoll and not id.endswith('/'):
            id = CannonicalId(id + '/')
        resource.id = six.text_type(id)  # override

        if id in self:
            old_etag = self[id].properties.get(('getetag', 'DAV:'))
        else:
            old_etag = None
        new_etag = resource.properties.get(('getetag', 'DAV:'))
        if new_etag and new_etag != old_etag:
            if (id not in self or
                    resource.data.read() != self[id].data.read()):
                raise zeit.connector.dav.interfaces.PreconditionFailedError()

        if id in self._deleted:
            self._deleted.remove(id)

        if not self._ignore_uuid_checks:
            existing_uuid = (
                id in self and self[id].properties.get(UUID_PROPERTY))
            new_uuid = resource.properties.get(UUID_PROPERTY)
            if not new_uuid:
                if existing_uuid:
                    new_uuid = existing_uuid
                else:
                    new_uuid = '{urn:uuid:%s}' % uuid.uuid4()
                resource.properties[UUID_PROPERTY] = new_uuid
            else:
                if existing_uuid and existing_uuid != new_uuid:
                    raise six.moves.http_client.HTTPException(409, 'Conflict')

            for key in self._properties.keys():
                if key == self._get_cannonical_id(resource.id):
                    continue
                existing_uuid = self._properties[key].get(UUID_PROPERTY)
                if (existing_uuid and existing_uuid ==
                        resource.properties[UUID_PROPERTY]):
                    raise six.moves.http_client.HTTPException(409, 'Conflict')

        # Just a very basic in-memory data storage for testing purposes.
        resource.data.seek(0)
        self._data[id] = resource.data.read()
        path = self._path(id)[:-1]
        name = self._path(id)[-1]
        self._paths.setdefault(path, set()).add(name)

        resource.properties[
            zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = resource.type
        if resource.contentType == 'httpd/unix-directory':
            # XXX kludgy. We need to be able to differentiate directories,
            # so they get a trailing slash in their CanonicalId, but also
            # don't want to store random content types, so the filemagic
            # detetection e.g. for images takes over on the next read.
            resource.properties[
                ('getcontenttype', 'DAV:')] = resource.contentType
        resource.properties[('getlastmodified', 'DAV:')] = six.text_type(
            datetime.datetime.now(pytz.UTC).strftime(
                '%a, %d %b %Y %H:%M:%S GMT'))
        resource.properties[('getetag', 'DAV:')] = repr(
            time.time()) + repr(random.random())

        self._set_properties(id, resource.properties)

        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))

    def __delitem__(self, id):
        id = self._get_cannonical_id(id)
        self[id]  # may raise KeyError
        for name, uid in self.listCollection(id):
            del self[uid]
        self._deleted.add(id)
        self._data.pop(id, None)
        self._properties.pop(id, None)
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))

    def add(self, object, verify_etag=True):
        resource = zeit.connector.interfaces.IResource(object)
        if not verify_etag:
            resource.properties.pop(('getetag', 'DAV:'), None)
        self[resource.id] = resource

    def copy(self, old_id, new_id):
        r = self[old_id]
        r.id = new_id
        r.properties.pop(UUID_PROPERTY, None)
        self.add(r, verify_etag=False)
        if not new_id.endswith('/'):
            new_id = new_id + '/'
        for name, uid in self.listCollection(old_id):
            self.copy(uid, six.moves.urllib.parse.urljoin(new_id, name))

    def move(self, old_id, new_id):
        if new_id in self:
            # The target already exists. It's possible that there was a
            # conflict. Verify body.
            if ('httpd/unix-directory' in (self[old_id].contentType,
                                           self[new_id].contentType) or
                    self[old_id].data.read() != self[new_id].data.read()):
                raise zeit.connector.interfaces.MoveError(
                    old_id,
                    "Could not move %s to %s, because target alread exists." %
                    (old_id, new_id))
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
            self.move(uid, six.moves.urllib.parse.urljoin(new_id, name))
        del self[old_id]

    def changeProperties(self, id, properties):
        id = self._get_cannonical_id(id)
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        id = self._get_cannonical_id(id)
        # locked_by, locked_until = self.locked(id)
        # if locked_by is not None and locked_by != principal:
        #    raise zeit.cms.interfaces.LockingError(
        #        "%s is already locked." % id)
        self._locked[id] = (principal, until, True)

    def unlock(self, id, locktoken=None):
        id = self._get_cannonical_id(id)
        del self._locked[id]
        return locktoken

    def locked(self, id):
        id = self._get_cannonical_id(id)
        return self._locked.get(id, (None, None, False))

    def search(self, attributes, expression):
        log.debug("Searching: %s", expression._render())

        unique_ids = [
            u'http://xml.zeit.de/online/2007/01/Somalia',
            u'http://xml.zeit.de/online/2007/01/Saarland',
            u'http://xml.zeit.de/2006/52/Stimmts']

        metadata = ('pm', '07') + len(attributes) * (None,)
        metadata = metadata[:len(attributes)]

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
        path = self._absolute_path(self._path(id))
        if os.path.isdir(path):
            return CannonicalId(id + '/')
        return CannonicalId(id)

    def _absolute_path(self, path):
        if not path:
            return self.repository_path
        return os.path.join(self.repository_path, os.path.join(*path))

    def _get_file(self, id):
        if id in self._data:
            value = self._data[id]
            if isinstance(value, six.text_type):
                value = value.encode('utf-8')
            return BytesIO(value)
        return super(Connector, self)._get_file(id)

    def _get_lastmodified(self, id):
        return u'Fri, 07 Mar 2008 12:47:16 GMT'

    def _get_properties(self, id):
        properties = self._properties.get(id)
        if properties is not None:
            return properties
        properties = super(Connector, self)._get_properties(id)
        self._properties[id] = properties
        return properties

    def _set_properties(self, id, properties):
        stored_properties = self._get_properties(id)
        for ((name, namespace), value) in properties.items():
            if (name.startswith('get') and name not in (
                    'getlastmodified', 'getetag', 'getcontenttype')):
                continue
            stored_properties[(name, namespace)] = value
            if value is zeit.connector.interfaces.DeleteProperty:
                del stored_properties[(name, namespace)]
        self._properties[id] = stored_properties


def connector_factory():
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    repository_path = (config or {}).get('repository-path')
    if not repository_path:
        repository_path = pkg_resources.resource_filename(
            __name__, 'testcontent')
    return Connector(repository_path)
