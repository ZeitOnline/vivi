from cStringIO import StringIO
from zeit.connector.connector import CannonicalId
from zeit.connector.dav.interfaces import DAVNotFoundError
import ZConfig
import ast
import email.utils
import gocept.cache.property
import logging
import lxml.etree
import os
import os.path
import urlparse
import zeit.connector.dav.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zope.app.appsetup.product
import zope.app.file.image
import zope.interface


ID_NAMESPACE = u'http://xml.zeit.de/'

log = logging.getLogger(__name__)


class Connector(object):
    """Connect to the CMS backend in read-only mode.

    The current implementation does *not* talk to the CMS backend but to
    a data store in the filesystem, the path to which needs to be configured.

    """

    zope.interface.implements(zeit.connector.interfaces.IConnector)

    resource_class = zeit.connector.resource.CachedResource
    canonicalize_directories = True

    _set_lastmodified_property = False

    property_cache = gocept.cache.property.TransactionBoundCache(
        '_v_property_cache', dict)
    body_cache = gocept.cache.property.TransactionBoundCache(
        '_v_body_cache', dict)
    child_name_cache = gocept.cache.property.TransactionBoundCache(
        '_v_child_name_cache', dict)
    canonical_id_cache = gocept.cache.property.TransactionBoundCache(
        '_v_canonical_id_cache', dict)

    def __init__(self, repository_path):
        self.repository_path = repository_path

    def listCollection(self, id):
        """List the filenames of a collection identified by path. """
        id = self._get_cannonical_id(id)
        try:
            return self.child_name_cache[id]
        except KeyError:
            pass

        path = self._path(id)
        names = self._get_collection_names(path)
        if not names:
            try:
                self[id]
            except KeyError:
                # XXX mimic the real behaviour -- real *should* probably raise
                # KeyError, but doesn't at the moment.
                raise DAVNotFoundError(404, 'Not Found', id, '')

        result = []
        for name in sorted(names):
            name = unicode(name)
            child_id = unicode(
                self._get_cannonical_id(self._make_id(path + (name, ))))
            result.append((name, child_id))
        self.child_name_cache[id] = result
        return result

    def _get_collection_names(self, path):
        absolute_path = self._absolute_path(path)
        names = (set(os.listdir(absolute_path))
                 if os.path.isdir(absolute_path) else set())
        for x in names.copy():
            if x.endswith('.meta') and x[:-5] in names:
                names.remove(x)
            if x.startswith('.'):
                names.remove(x)
        return names

    def getResourceType(self, id):
        id = self._get_cannonical_id(id)
        __traceback_info__ = id

        properties = self._get_properties(id)
        if properties:
            type = properties.get(
                zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY)
            if type:
                return type

        path = self._absolute_path(self._path(id))
        if os.path.isdir(path):
            return 'collection'

        f = self._get_file(id)
        data = f.read(200)
        f.close()
        content_type, width, height = zope.app.file.image.getImageInfo(data)
        if content_type:
            return 'image'
        return 'unknown'

    def __getitem__(self, id):
        id = self._get_cannonical_id(id)
        properties = self._get_properties(id)
        type = self.getResourceType(id)
        properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = type
        path = self._path(id)
        name = path[-1] if path else ''
        return self.resource_class(
            unicode(id), name, type,
            lambda: self._get_properties(id),
            lambda: self._get_body(id),
            content_type=self._get_content_type(id, type))

    def _get_body(self, id):
        try:
            return StringIO(self.body_cache[id])
        except KeyError:
            pass
        try:
            f = self._get_file(id)
            data = f.read()
            f.close()
        except:
            data = ''
        self.body_cache[id] = data
        return StringIO(data)

    def _get_content_type(self, id, type):
        return 'httpd/unix-directory' if type == 'collection' else ''

    def __setitem__(self, id, object):
        raise NotImplementedError()

    def __delitem__(self, id):
        raise NotImplementedError()

    def __contains__(self, id):
        try:
            self[id]
        except KeyError:
            return False
        return True

    def add(self, object, verify_etag=True):
        raise NotImplementedError()

    def copy(self, old_id, new_id):
        raise NotImplementedError()

    def move(self, old_id, new_id):
        raise NotImplementedError()

    def changeProperties(self, id, properties):
        raise NotImplementedError()

    def lock(self, id, principal, until):
        raise NotImplementedError()

    def unlock(self, id, locktoken=None):
        raise NotImplementedError()

    def locked(self, id):
        raise NotImplementedError()

    def search(self, attributes, expression):
        raise NotImplementedError()

    # internal helpers

    def _get_cannonical_id(self, id):
        """Add / for collections if not appended yet."""
        if isinstance(id, CannonicalId):
            return id
        if id == ID_NAMESPACE:
            return CannonicalId(id)

        input = id
        result = id
        try:
            return self.canonical_id_cache[input]
        except KeyError:
            pass

        if result.endswith('/'):
            result = result[:-1]
        if self.canonicalize_directories:
            path = self._absolute_path(self._path(result))
            if os.path.isdir(path):
                result = CannonicalId(result + '/')
        else:
            result = CannonicalId(result)
        self.canonical_id_cache[input] = result
        return result

    def _absolute_path(self, path):
        if not path:
            return self.repository_path
        return os.path.join(self.repository_path, os.path.join(*path))

    def _path(self, id):
        if not id.startswith(ID_NAMESPACE):
            raise ValueError("The id %r is invalid." % id)
        id = id.replace(ID_NAMESPACE, '', 1)
        if not id:
            return ()
        result = tuple(id.split('/'))
        if result[-1] == '':
            result = result[:-1]
        return result

    def _get_file(self, id):
        filename = self._absolute_path(self._path(id))
        __traceback_info__ = (id, filename)
        try:
            return file(filename, 'rb')
        except IOError:
            if os.path.isdir(filename):
                raise ValueError(
                    'The path %r points to a directory.' % filename)
            raise KeyError("The resource '%s' does not exist." % id)

    def _get_metadata_file(self, id):
        filename = self._absolute_path(self._path(id)) + '.meta'
        __traceback_info__ = (id, filename)
        try:
            return file(filename, 'rb')
        except IOError:
            return self._get_file(id)

    def _make_id(self, path):
        return urlparse.urljoin(ID_NAMESPACE, '/'.join(
            element for element in path if element))

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
        try:
            data = self._get_metadata_file(id)
            xml = lxml.etree.parse(data)
            data.close()
        except ValueError:
            # Performance optimization: We know this error happens only for
            # directories, so we can determine the resource type here instead
            # of waiting for getResourceType() doing the isdir check _again_.
            properties[zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY] = (
                'collection')
            metadata_parse_error = True
        except lxml.etree.LxmlError:
            metadata_parse_error = True
        if metadata_parse_error:
            self.property_cache[id] = properties
            return properties

        nodes = xml.xpath('//head/attribute')
        for node in nodes:
            properties[node.get('name'), node.get('ns')] = node.text or ''

        # rankedTags are serialized like all other attributes in .meta files,
        # but in the "fallback to content file" case we need to recognize a
        # different format:
        tags = xml.xpath('//head/rankedTags')
        if tags:
            value = (
                '<tag:rankedTags xmlns:tag="http://namespaces.zeit.de'
                '/CMS/tagging">')
            value += lxml.etree.tostring(tags[0])
            value += '</tag:rankedTags>'
            properties[(
                'rankedTags',
                'http://namespaces.zeit.de/CMS/tagging')] = value

        self.property_cache[id] = properties
        return properties

    def _get_lastmodified(self, id):
        filename = self._absolute_path(self._path(id))
        try:
            mtime = os.stat(filename).st_mtime
        except OSError:
            return None
        return email.utils.formatdate(mtime, usegmt=True)


def connector_factory():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector') or {}
    repository_path = config.get('repository-path')
    if not repository_path:
        raise ZConfig.ConfigurationError(
            "Filesystem connector not configured properly.")
    connector = Connector(repository_path)
    canonicalize = config.get('canonicalize-directories', None)
    if canonicalize is not None:
        connector.canonicalize_directories = ast.literal_eval(canonicalize)
    return connector
