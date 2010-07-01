# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connect to the CMS backend."""

from zeit.connector.interfaces import UUID_PROPERTY
import StringIO
import datetime
import httplib
import lxml.etree
import os
import os.path
import pytz
import time
import urlparse
import uuid
import zeit.connector.dav.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zope.app.file.image
import zope.event
import zope.interface


ID_NAMESPACE = u'http://xml.zeit.de/'

repository_path = os.path.join(os.path.dirname(__file__), 'testcontent')


class Connector(object):
    """Connect to the CMS backend.

    The current implementation does *not* talk to the CMS backend but to
    some directory containing test content.

    """

    zope.interface.implements(zeit.connector.interfaces.IConnector)

    _ignore_uuid_checks = False

    def __init__(self):
        self._reset()

    def _reset(self):
        self._locked = {}
        self._data = {}
        self._paths = {}
        self._deleted = set()
        self._properties = {}
        self._content_types = {}

    def listCollection(self, id):
        """List the filenames of a collection identified by path. """
        path = self._path(id)
        absolute_path = self._absolute_path(path)
        names = set()
        if os.path.isdir(absolute_path):
            names = names | set(os.listdir(self._absolute_path(path)))
        names = names | self._paths.get(path, set())
        for name in sorted(names):
            name = unicode(name)
            if name.startswith('.'):
                continue
            id = self._make_id(path + (name, ))
            if id in self._deleted:
                continue
            yield (name, id)

    def getResourceType(self, id):
        __traceback_info__ = id
        path = self._absolute_path(self._path(id))
        if id in self._deleted:
            raise KeyError("The resource %r does not exist." % id)
        if os.path.isdir(path):
            return 'collection'
        data = self._get_file(id).read(200)
        if '<article>' in data:
            # Ok, this is hardcore. But it's not production code, is it.
            return 'article'
        if '<channel>' in data:
            return 'channel'
        if '<centerpage>' in data:
            return 'centerpage'
        if '<testtype>' in data:
            return 'testcontenttype'
        content_type, width, height = zope.app.file.image.getImageInfo(data)
        if content_type:
            return 'image'
        return 'unknown'

    def __getitem__(self, id):
        if id in self._deleted:
            raise KeyError(id)
        properties = self._get_properties(id)
        type = properties.get(
            zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY)
        if type is None:
            type = self.getResourceType(id)
            properties[
                zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = type
        if type == 'collection':
            data = StringIO.StringIO()
        else:
            data = self._get_file(id)
        path = self._path(id)
        if path:
            name = path[-1]
        else:
            name = ''
        return zeit.connector.resource.Resource(
            id, name, type, data, properties,
            contentType=self._content_types.get(id, ''))

    def __setitem__(self, id, object):
        resource = zeit.connector.interfaces.IResource(object)

        if id in self:
            old_etag = self[id].properties.get(('getetag', 'DAV:'))
        else:
            old_etag = None
        new_etag = resource.properties.get(('getetag', 'DAV:'))
        if new_etag and new_etag != old_etag:
            if (id not in self
                or resource.data.read() != self[id].data.read()):
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
                    raise httplib.HTTPException(409, 'Conflict')

            for key in self._properties.keys():
                if key == resource.id:
                    continue
                existing_uuid = self._properties[key].get(UUID_PROPERTY)
                if (existing_uuid and existing_uuid ==
                    resource.properties[UUID_PROPERTY]):
                    raise httplib.HTTPException(409, 'Conflict')

        # Just a very basic in-memory data storage for testing purposes.
        resource.data.seek(0)
        self._data[id] = resource.data.read()
        path = self._path(id)[:-1]
        name = self._path(id)[-1]
        self._paths.setdefault(path, set()).add(name)

        resource.properties[
            zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = resource.type
        resource.properties[('getlastmodified', 'DAV:')] = unicode(
            datetime.datetime.now(pytz.UTC).strftime(
                '%a, %d %b %Y %H:%M:%S GMT'))
        resource.properties[('getetag', 'DAV:')] = repr(time.time())

        self._set_properties(id, resource.properties)
        self._content_types[id] = resource.contentType

        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))

    def __delitem__(self, id):
        resource = self[id]
        for name, uid in self.listCollection(id):
            del self[uid]
        self._deleted.add(id)
        self._data.pop(id, None)
        self._properties.pop(id, None)
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))

    def __contains__(self, id):
        try:
            resource = self[id]
        except KeyError:
            return False
        return True

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
            self.copy(uid, urlparse.urljoin(new_id, name))

    def move(self, old_id, new_id):
        if new_id in self:
            raise zeit.connector.interfaces.MoveError(
                old_id,
                "Could not move %s to %s, because target alread exists." % (
                    old_id, new_id))
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
            self.move(uid, urlparse.urljoin(new_id, name))
        del self[old_id]


    def changeProperties(self, id, properties):
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        #locked_by, locked_until = self.locked(id)
        #if locked_by is not None and locked_by != principal:
        #    raise zeit.cms.interfaces.LockingError(
        #        "%s is already locked." % id)
        self._locked[id] = (principal, until, True)

    def unlock(self, id, locktoken=None):
        del self._locked[id]
        return locktoken

    def locked(self, id):
        return self._locked.get(id, (None, None, False))

    def search(self, attributes, expression):
        print  "Searching: ", expression._collect()._render()

        unique_ids = [
            u'http://xml.zeit.de/online/2007/01/Somalia',
            u'http://xml.zeit.de/online/2007/01/Saarland',
            u'http://xml.zeit.de/2006/52/Stimmts']

        metadata = ('pm', '07') + len(attributes) * (None,)
        metadata = metadata[:len(attributes)]

        return ((unique_id,) + metadata for unique_id in unique_ids)

    # internal helpers

    def _absolute_path(self, path):
        if not path:
            return repository_path
        return os.path.join(repository_path, os.path.join(*path))

    def _path(self, id):
        if not id.startswith(ID_NAMESPACE):
            raise ValueError("The id %r is invalid." % id)
        id = id.replace(ID_NAMESPACE, '', 1)
        if not id:
            return ()
        return tuple(id.split('/'))

    def _get_file(self, id):
        if id in self._data:
            return StringIO.StringIO(self._data[id])
        filename = self._absolute_path(self._path(id))
        __traceback_info__ = (id, filename)
        try:
            return file(filename, 'rb')
        except IOError:
            raise KeyError("The resource %r does not exist." % id)

    def _make_id(self, path):
        return urlparse.urljoin(ID_NAMESPACE, '/'.join(
            element for element in path if element))

    def _get_properties(self, id):
        properties = self._properties.get(id)
        if properties is not None:
            return properties
        properties = {}
        # We have not properties for this type, try to read it from the file.
        # This is sort of a hack, but we need it to get properties at all
        if self.getResourceType(id) != 'collection':
            data = self._get_file(id)
            try:
                xml = lxml.etree.parse(data)
            except lxml.etree.LxmlError:
                pass
            else:
                nodes = xml.xpath('//head/attribute')
                for node in nodes:
                    properties[node.get('name'), node.get('ns')] = (
                        node.text)
        properties[('getlastmodified', 'DAV:')] = (
            u'Fri, 07 Mar 2008 12:47:16 GMT')
        self._properties[id] = properties
        return properties

    def _set_properties(self, id, properties):
        stored_properties = self._get_properties(id)
        for ((name, namespace), value) in properties.items():
            if (name.startswith('get')
                and name not in ('getlastmodified', 'getetag')):
                continue
            stored_properties[(name, namespace)] = value
            if value is zeit.connector.interfaces.DeleteProperty:
                del stored_properties[(name, namespace)]
        self._properties[id] = stored_properties
