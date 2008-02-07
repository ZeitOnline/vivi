# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.interface.common.mapping
import zope.schema


class _DeleteProperty(object):
    """Singleton to indicate a property should be deleted."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'DeleteProperty'

    def __reduce__(self):
        return (_DeleteProperty, ())


DeleteProperty = _DeleteProperty()


class ConnectorError(Exception):
    """Generic, resource related, error in the connector."""

    def __init__(self, id, *args):
        self.uniqueId = id
        self.args = args


class LockingError(ConnectorError):
    """Raised when trying to lock an already locked resource."""


class MoveError(ConnectorError):
    """Raised when moving an object fails."""


class LockedByOtherSystemError(LockingError):
    """Raised when trying to update an resource which was not locked by us.
    """


class IConnector(zope.interface.Interface):
    """Connects the cms to the backend.

    This utility interfaces the CMSConnector provided by Thomas, Ralf, etc.

    """

    def listCollection(id):
        """List the contents of collection.

        id: unique id of the colleciton to list

        returns sequence of (local_id, unique_id). The unique ids normally
        have a form like
        `http://xml.zeit.de/(online)?/[Jahr]/[Ausgabe]/[Artikelname]` but
        callers should *not* rely on that.

        raises ValueError if the id is not valid or does not match the
         repository.
        raises KeyError if the resource does not exist.

        XXX define more error cases
        """


    def __getitem__(id):
        """Return the resource identified by `id`.

        returns an IResource instance.

        raises KeyError if the resource could not be found.

        """

    def __delitem__(id):
        """Remove the resource from the repository.

        raises KeyError if the resource could not be found.

        """

    def __setitem__(id, object):
        """Add the given `object` to the document store under the given name.

        The object must be adaptable to IResource.

        """

    def __contains__(id):
        """Return whether resource `id` exists."""

    def add(object):
        """Add the given `object` to the document store.

        The object must be adaptable to IResource.

        """

    def move(old_id, new_id):
        """Move the resource with id `old_id` to `new_id`.

        raises KeyError if ther is no resource `old_id`
        raises MoveError if there was a problem with moving itself.

        """

    def changeProperties(id, properties):
        """Change webdav properties of object.

        id: unique id
        properties: see IWebDAVProperties.properties

        """

    def lock(id, principal, until):
        """Lock resource for principal until a given datetime.

        id: unique id
        until: datetime until the lock is valid.

        """

    def unlock(id):
        """Unlock resource."""

    def locked(id):
        """Return whether a resource is locked or not.

        returns tuple <lock owner>, <locked until>, <my lock>
            lock owner: principal id
            locked until: datetime.datetime instance
            my lock: True if the lock was issued by this system, False
                otherwise.

        returns None, None, None if the resource is not locked.
        raises KeyError if the resource does not exist.

        """

    def search(attributes, search_expression):
        """Search for `search_expression`

        returns an iterator of tuples containing the unique id and the values
        of the requested `attributes`:

            (unique_id, attributes[0], attributes[1], ...)

        """

class IWebDAVReadProperties(zope.interface.common.mapping.IEnumerableMapping):
    """Mapping for WebDAV properties.

    Keys are in the form (name, namespace), for example:

        {(u'resourcetype', u'DAV:'): u'article'}

    name, namespace and value should be unicode. If any is a str it must not
    contain non usascii characters.

    value can be the special value of DeleteProperty to indicate the property
    should be removed.

    """

class IWebDAVWriteProperties(
    zope.interface.common.mapping.IExtendedWriteMapping):
    """Write interface for WebDAVProperties."""


class IWebDAVProperties(IWebDAVReadProperties, IWebDAVWriteProperties):
    """Combined read and write interface for webdav properties."""


class IResource(zope.interface.Interface):
    """Represents a resource in the webdav.

    This is the resource interface the connector uses to return or get
    resources.
    """

    __name__ = zope.schema.TextLine(
        title=u"The name within the parent",
        description=u"Traverse the parent with this name to get the object.")

    # TODO: make this an URI. We want the unique ids to not contain any unicode
    # characters, so a URI would be the right thing. Right now we have unicode
    # unique ids though makeing URI invalid.
    id = zope.interface.Attribute("Unique id of resource")

    # TODO: make type a choice. This requires a source for valid types. We
    # might want to use the interface dotted name instead of just 'article' or
    # 'image'.
    type = zope.interface.Attribute("Resource type (folder, image, ...).")

    data = zope.interface.Attribute(
        u"Resource main data (body, image data) as a file-like object.")
    contentType = zope.schema.BytesLine(
        title=u"Content Type",
        description=u'The mime content type identifies the type of data.',
        default='',
        required=False)

    properties = zope.schema.Object(
        IWebDAVProperties,
        title=u"WebDAV properties")



class IResourceCache(zope.interface.Interface):
    """A cache for resource data.

    XXX out of date"""

    def getData(unique_id, dav_resource):
        """Return data for given unique_id and dav_resource.

        The data will cached before it is returned. If the data is cached it
        will be returned from the cache.

        The cache will be automatically invalidated if the etag of the resouce
        changes.

        """
