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
        self._reset()
        self.repository_path = repository_path

    def _reset(self):
        self._properties = {}
        self._content_types = {}

    def listCollection(self, id):
        """List the filenames of a collection identified by path. """
        try:
            self[id]
        except KeyError:
            # XXX mimic the real behaviour -- real *should* probably raise
            # KeyError, but doesn't at the moment.
            raise DAVNotFoundError(404, 'Not Found', id, '')
        path = self._path(id)
        absolute_path = self._absolute_path(path)
        names = set()
        if os.path.isdir(absolute_path):
            names = names | set(os.listdir(self._absolute_path(path)))
        for name in sorted(names):
            name = unicode(name)
            if name.startswith('.'):
                continue
            id = self._make_id(path + (name, ))
            yield (name, id)

    def getResourceType(self, id):
        __traceback_info__ = id
        path = self._absolute_path(self._path(id))
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
        content_type = self._content_types.get(id, '')
        if not content_type and type == 'collection':
            content_type = 'httpd/unix-directory'
        return zeit.connector.resource.Resource(
            id, name, type, data, properties,
            contentType=content_type)

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
        filename = self._absolute_path(self._path(id))
        mtime = os.stat(filename).st_mtime
        properties[('getlastmodified', 'DAV:')] = (
            email.utils.formatdate(mtime, usegmt=True))
        self._properties[id] = properties
        return properties


def connector_factory():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    repository_path = (config or {}).get('repository-path')
    if not repository_path:
        raise ZConfig.ConfigurationError(
            "Filesystem connector not configured properly.")
    return Connector(repository_path)
