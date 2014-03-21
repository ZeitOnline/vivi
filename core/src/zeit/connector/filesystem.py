# Copyright (c) 2007-2013 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connect to data stored in the filesystem in read-only mode."""

from zeit.connector.dav.interfaces import DAVNotFoundError
import StringIO
import ZConfig
import email.utils
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

    def __init__(self, repository_path):
        self.repository_path = repository_path

    def listCollection(self, id):
        """List the filenames of a collection identified by path. """
        try:
            self[id]
        except KeyError:
            # XXX mimic the real behaviour -- real *should* probably raise
            # KeyError, but doesn't at the moment.
            raise DAVNotFoundError(404, 'Not Found', id, '')
        path = self._path(id)
        names = self._get_collection_names(path)
        for name in sorted(names):
            name = unicode(name)
            if name.startswith('.'):
                continue
            id = self._make_id(path + (name, ))
            yield (name, id)

    def _get_collection_names(self, path):
        absolute_path = self._absolute_path(path)
        names = (set(os.listdir(absolute_path))
                 if os.path.isdir(absolute_path) else set())
        for x in names.copy():
            if x.endswith('.meta') and x[:-5] in names:
                names.remove(x)
        return names

    def getResourceType(self, id):
        __traceback_info__ = id
        path = self._absolute_path(self._path(id))
        if os.path.isdir(path):
            return 'collection'

        properties = self._get_properties(id)
        if properties:
            type = properties.get(
                zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY)
            if type:
                return type

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
        content_type = self._get_content_type(id, type)
        return zeit.connector.resource.Resource(
            id, name, type, data, properties,
            contentType=content_type)

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
        return tuple(id.split('/'))

    def _get_file(self, id):
        filename = self._absolute_path(self._path(id))
        __traceback_info__ = (id, filename)
        if os.path.isdir(filename):
            raise ValueError('The path %r points to a directory.' % filename)
        try:
            return file(filename, 'rb')
        except IOError:
            raise KeyError("The resource %r does not exist." % id)

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
        properties = {}
        modified = self._get_lastmodified(id)
        if modified:
            properties[('getlastmodified', 'DAV:')] = modified

        try:
            data = self._get_metadata_file(id)
            xml = lxml.etree.parse(data)
        except (ValueError, lxml.etree.LxmlError):
            return properties

        nodes = xml.xpath('//head/attribute')
        for node in nodes:
            properties[node.get('name'), node.get('ns')] = node.text

        # XXX workaround for zeit.frontend, can probably go away
        # once the filesystem connector is finished.
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
        'zeit.connector')
    repository_path = (config or {}).get('repository-path')
    if not repository_path:
        raise ZConfig.ConfigurationError(
            "Filesystem connector not configured properly.")
    return Connector(repository_path)
