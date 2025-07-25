from io import BytesIO
from urllib.parse import urlparse
import email.utils
import logging
import os
import os.path
import xml.sax.saxutils

import gocept.cache.property
import lxml.etree
import zope.app.file.image
import zope.interface

from zeit.connector.interfaces import ID_NAMESPACE, DeleteProperty
from zeit.connector.postgresql import Connector as SQLConnector
import zeit.cms.config
import zeit.cms.content.dav
import zeit.connector.converter
import zeit.connector.interfaces
import zeit.connector.resource


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
class Connector:
    """Connect to the CMS backend in read-only mode.

    The current implementation does *not* talk to the CMS backend but to
    a data store in the filesystem, the path to which needs to be configured.
    """

    resource_class = zeit.connector.resource.CachedResource

    _set_lastmodified_property = False

    property_cache = gocept.cache.property.TransactionBoundCache('_v_property_cache', dict)
    body_cache = gocept.cache.property.TransactionBoundCache('_v_body_cache', dict)
    child_name_cache = gocept.cache.property.TransactionBoundCache('_v_child_name_cache', dict)

    def __init__(self, repository_path):
        # Support `egg://` product config from zeit.cms.zope
        repository_path = repository_path.replace('file://', '', 1)
        self.repository_path = repository_path

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        config = zeit.cms.config.package('zeit.connector')
        return cls(config['repository-path'])

    def listCollection(self, id):
        """List the filenames of a collection identified by path."""
        id = SQLConnector._normalize(id)
        try:
            return self.child_name_cache[id]
        except KeyError:
            pass

        path = self._path(id)
        names = self._get_collection_names(path)
        if not names:
            self[id]

        result = []
        for name in sorted(names):
            child_id = os.path.join(id, name)
            result.append((name, child_id))
        self.child_name_cache[id] = result
        return result

    def _get_collection_names(self, path):
        names = set()

        if os.path.isdir(path):
            for name in os.listdir(path):
                try:
                    if isinstance(name, bytes):
                        name = name.decode('utf-8')
                except Exception:
                    continue
                names.add(name)
        for x in names.copy():
            if x.startswith('.'):
                names.remove(x)
            elif x.endswith('.meta') and x[:-5] in names:
                names.remove(x)
        return names

    def __getitem__(self, id):
        id = SQLConnector._normalize(id)
        properties = self._get_properties(id)
        path = urlparse(id).path.strip('/').split('/')
        return self.resource_class(
            str(id),
            path[-1],
            properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY],
            lambda: self._get_properties(id),
            lambda: self._get_body(id),
            self._is_collection(id),
        )

    def _get_body(self, id):
        try:
            return BytesIO(self.body_cache[id])
        except KeyError:
            pass
        try:
            f = self._get_file(id)
            data = f.read()
            f.close()
        except Exception:
            data = b''
        self.body_cache[id] = data
        return BytesIO(data)

    def _is_collection(self, id):
        properties = self._get_properties(id)
        if properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] == 'collection':
            return True
        davtype = ('getcontenttype', 'DAV:')
        return properties.get(davtype, '') == 'httpd/unix-directory'

    def __setitem__(self, id, resource):
        id = SQLConnector._normalize(id)
        resource.id = id
        self.add(resource)

    def __delitem__(self, id):
        raise NotImplementedError()

    def __contains__(self, id):
        try:
            self[id]
        except KeyError:
            return False
        return True

    def add(self, resource, verify_etag=True):
        self._write_metadata_file(resource.id, resource.properties)

        if resource.is_collection:
            os.makedirs(self._path(resource.id), exist_ok=True)
        else:
            with self._get_file(resource.id, 'wb') as f:
                while chunk := resource.data.read(self.WRITE_CHUNK_SIZE):
                    f.write(chunk)

    WRITE_CHUNK_SIZE = 8 * 1024

    def copy(self, old_id, new_id):
        raise NotImplementedError()

    def move(self, old_id, new_id):
        raise NotImplementedError()

    def changeProperties(self, id, properties):
        id = SQLConnector._normalize(id)
        resource = self[id]
        current = dict(resource.properties)
        current.update(properties)
        self._write_metadata_file(id, current)

    def lock(self, id, principal, until):
        raise NotImplementedError()

    def unlock(self, id, locktoken=None):
        raise NotImplementedError()

    def locked(self, id):
        raise NotImplementedError()

    def search(self, attributes, expression):
        log.warning('NotImplemented search(%s)', expression._render())
        return ()

    # internal helpers

    def _path(self, id):
        if id == ID_NAMESPACE.rstrip('/'):
            return self.repository_path
        path = id.replace(ID_NAMESPACE, '', 1).rstrip('/')
        return os.path.join(self.repository_path, path).rstrip('/')

    def _get_file(self, id, mode='rb'):
        filename = self._path(id)
        __traceback_info__ = (id, filename)
        try:
            return open(filename, mode)
        except IOError:
            if os.path.isdir(filename):
                raise ValueError('The path %r points to a directory.' % filename)
            raise KeyError("The resource '%s' does not exist." % id)

    def _get_metadata_file(self, id, mode='rb'):
        filename = self._path(id) + '.meta'
        __traceback_info__ = (id, filename)
        try:
            return open(filename, mode)
        except IOError:
            if not id.endswith('.meta'):
                return self._get_file(id)
            return BytesIO(b'')

    def _get_properties(self, id):
        try:
            return self.property_cache[id]
        except KeyError:
            pass
        properties = {}
        if self._set_lastmodified_property:
            modified = self._get_lastmodified(id)
            if modified:
                properties[('getlastmodified', 'DAV:')] = modified

        metadata_parse_error = False
        data = None
        try:
            data = self._get_metadata_file(id)
            xml = lxml.etree.parse(data)
        except ValueError:
            properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = 'collection'
            metadata_parse_error = True
        except lxml.etree.LxmlError:
            properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = self._guess_type(id)
            metadata_parse_error = True
        finally:
            if data is not None:
                data.close()
        if metadata_parse_error:
            self.property_cache[id] = properties
            return properties

        properties.update(parse_properties(xml))

        if zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY not in properties:
            properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = self._guess_type(id)

        self.property_cache[id] = properties
        return properties

    def _guess_type(self, id):
        path = self._path(id)
        if os.path.isdir(path):
            return 'collection'

        f = self._get_file(id)
        data = f.read(200)
        f.close()
        content_type, width, height = zope.app.file.image.getImageInfo(data)
        if content_type:
            return 'image'
        return 'unknown'

    def mtime(self, id, suffix=''):
        filename = self._path(id) + suffix
        try:
            mtime = os.stat(filename).st_mtime
        except OSError:
            return None
        return mtime

    def _get_lastmodified(self, id):
        mtime = self.mtime(id)
        return email.utils.formatdate(mtime, usegmt=True)

    def _write_metadata_file(self, id, properties):
        with self._get_metadata_file(id, 'w') as f:
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            f.write('<head>\n')
            for (name, ns), value in properties.items():
                if value is DeleteProperty or value is None:
                    continue
                value = xml.sax.saxutils.escape(value)
                f.write(f'  <attribute ns="{ns}" name="{name}">{value}</attribute>\n')
            f.write('</head>\n')


factory = Connector.factory


def parse_properties(xml):
    properties = {}
    nodes = xml.xpath('//head/attribute')
    for node in nodes:
        properties[node.get('name'), node.get('ns')] = node.text or ''

    # rankedTags are serialized like all other attributes in .meta files,
    # but in the "fallback to content file" case we need to recognize a
    # different format:
    tags = xml.xpath('//head/rankedTags')
    if tags:
        value = '<tag:rankedTags xmlns:tag="http://namespaces.zeit.de/CMS/tagging">'
        value += lxml.etree.tostring(tags[0], encoding=str)
        value += '</tag:rankedTags>'
        properties[('keywords', 'http://namespaces.zeit.de/CMS/tagging')] = value
    return properties
