# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Connect to the CMS backend."""

import StringIO
import datetime
import os
import os.path
import urlparse

import lxml.etree
import gocept.lxml.objectify

import persistent.mapping

import zope.interface

import zope.app.locking.interfaces
import zope.app.file.image

import zeit.cms.interfaces


ID_NAMESPACE = zeit.cms.interfaces.ID_NAMESPACE

repository_path = os.path.join(os.path.dirname(__file__), 'testcontent')


class Connector(object):
    """Connect to the CMS backend.

    The current implementation does *not* talk to the CMS backend but to
    some directory containing test content.

    """

    zope.interface.implements(zeit.cms.interfaces.IConnector)

    def __init__(self):
        self._locked = {}
        self._data = {}
        self._paths = {}
        self._deleted = set()
        self._properties = {}

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
        if '<feed xmlns="http://namespaces.zeit.de/CMS/feed">' in data:
            return 'feed'
        if '<centerpage>' in data:
            return 'centerpage'
        content_type, width, height = zope.app.file.image.getImageInfo(data)
        if content_type:
            return 'image'
        return 'unknown'

    def __getitem__(self, id):
        properties = self._get_properties(id)
        type = properties.get(('resourcetype', 'DAV:'))
        if type is None:
            type = self.getResourceType(id)
            properties[('resourcetype', 'DAV:')] = type
        if type == 'collection':
            data = None
        else:
            data = self._get_file(id)
        return Resource(id, self._path(id)[-1], type, data, properties)

    def __setitem__(self, id, object):
        resource = zeit.cms.interfaces.IResource(object)
        # Just a very basic in-memory data storage for testing purposes.
        resource.data.seek(0)
        self._data[id] = resource.data.read()
        path = self._path(id)[:-1]
        name = self._path(id)[-1]
        self._paths.setdefault(path, set()).add(name)
        resource.properties[('resourcetype', 'DAV:')] = resource.type
        self._set_properties(id, resource.properties)

    def __delitem__(self, id):
        resource = self[id]
        self._deleted.add(id)

    def add(self, object):
        resource = zeit.cms.interfaces.IResource(object)
        self[resource.id] = resource

    def changeProperties(self, id, properties):
        self._set_properties(id, properties)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        #locked_by, locked_until = self.locked(id)
        #if locked_by is not None and locked_by != principal:
        #    raise zeit.cms.interfaces.LockingError(
        #        "%s is already locked." % id)
        self._locked[id] = (principal, until, True)

    def unlock(self, id):
        del self._locked[id]

    def locked(self, id):
        return self._locked.get(id, (None, None, None))

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
        return urlparse.urljoin(ID_NAMESPACE, '/'.join(path))

    def _get_properties(self, id):
        properties = self._properties.get(id)
        if properties is not None:
            return properties
        # We have not properties for this type, try to read it from the file.
        # This is sort of a hack, but we need it to get properties at all
        if self.getResourceType(id) == 'collection':
            return {}
        data = self._get_file(id)
        properties = {}
        try:
            xml = lxml.etree.parse(data)
        except lxml.etree.LxmlError:
            pass
        else:
            nodes = xml.xpath('//head/attribute')
            for node in nodes:
                properties[node.get('name'), node.get('ns')] = (
                    node.text)
        self._properties[id] = properties
        return properties

    def _set_properties(self, id, properties):
        stored_properties = self._get_properties(id)
        for ((name, namespace), value) in properties.items():
            if name.startswith('get'):
                continue
            stored_properties[(name, namespace)] = value
            if value is zeit.cms.interfaces.DeleteProperty:
                del stored_properties[(name, namespace)]
        self._properties[id] = stored_properties


class WebDAVProperties(persistent.mapping.PersistentMapping):

    zope.interface.implements(zeit.cms.interfaces.IWebDAVProperties)

    def __repr__(self):
        return object.__repr__(self)


class Resource(object):
    """Represents a resource in the webdav."""

    zope.interface.implements(zeit.cms.interfaces.IResource)

    def __init__(self, id, name, type, data, properties=None, contentType=''):
        self.id = id
        self.__name__ = name
        self.type = type
        self.data = data
        if properties is None:
            properties = {}
        self.properties = WebDAVProperties(properties)
        self.contentType = contentType


def xmlContentToResourceAdapterFactory(typ):
    """Adapt content type to IResource"""

    @zope.interface.implementer(zeit.cms.interfaces.IResource)
    def adapter(context):
        try:
            properties = zeit.cms.interfaces.IWebDAVReadProperties(context)
        except TypeError:
            properties = WebDAVProperties()
        return Resource(
            context.uniqueId, context.__name__, typ,
            data=StringIO.StringIO(context.xml_source),
            contentType='text/xml',
            properties=properties)

    return adapter


class LockStorage(object):

    zope.interface.implements(zope.app.locking.interfaces.ILockStorage)

    def getLock(self, object):
        try:
            locked_by, locked_until, my_lock = self.connector.locked(
                object.uniqueId)
        except KeyError:
            # resource does not exist -> no lock
            return None
        if locked_by is None:
            return None
        delta = locked_until - datetime.datetime.now()
        timeout = (delta.days * 86400
                   + delta.seconds
                   + delta.microseconds * 1e-6)
        return zope.app.locking.lockinfo.LockInfo(None, locked_by, timeout)

    def setLock(self, object, lock):
        until = datetime.datetime.fromtimestamp(lock.created + lock.timeout)
        self.connector.lock(object.uniqueId, lock.principal_id, until)

    def delLock(self, object):
        self.connector.unlock(object.uniqueId)

    def cleanup(self):
        pass

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)
