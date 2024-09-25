from enum import Enum

import zope.interface
import zope.interface.common.mapping
import zope.schema


class _DeleteProperty:
    """Singleton to indicate a property should be deleted."""

    __slots__ = ()
    _instance = None  # class variable

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'DeleteProperty'

    def __reduce__(self):
        return (_DeleteProperty, ())


DeleteProperty = _DeleteProperty()

try:
    import zope.security.checker

    # Make DeleteProperty a rock
    zope.security.checker.BasicTypes[_DeleteProperty] = zope.security.checker.NoProxy
except ImportError:
    pass  # soft dependency


ID_NAMESPACE = 'http://xml.zeit.de/'

RESOURCE_TYPE_PROPERTY = ('type', 'http://namespaces.zeit.de/CMS/meta')
UUID_PROPERTY = ('uuid', 'http://namespaces.zeit.de/CMS/document')
INTERNAL_PROPERTY = 'INTERNAL'
CACHED_TIME_PROPERTY = ('cached-time', INTERNAL_PROPERTY)


class ConnectorError(Exception):
    """Generic, resource related, error in the connector."""

    def __init__(self, id, *args):
        self.uniqueId = id
        self.args = args


class LockingError(ConnectorError):
    """Raised when trying to lock an already locked resource."""


class CopyError(ConnectorError):
    """Raised when copying an object fails."""


class MoveError(ConnectorError):
    """Raised when moving an object fails."""


class LockedByOtherSystemError(LockingError):
    """Raised when trying to update an resource which was not locked by us."""


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
        """

    def __getitem__(id):
        """Return the resource identified by `id`.

        returns an IResource instance.

        raises KeyError if the resource could not be found.
        """

    def __delitem__(id):
        """Remove the resource from the repository.

        raises KeyError if the resource could not be found.
        raises LockedByOtherSystemError if the resource is locked by another user
        """

    def __setitem__(id, object):
        """Add the given `object` to the document store under the given name.

        The object must be adaptable to IResource.
        """

    def __contains__(id):
        """Return whether resource `id` exists."""

    def add(object, verify_etag=True):
        """Add the given `object` to the document store.

        The object must be adaptable to IResource.

        If verify_etag is True (the default) an {DAV:}getetag in the resource's
        properties is added to a conditional ``If:`` header so adding only
        succeeds when the given etag matches the etag on the DAV server.

        Raises PreconditionFailedError if verify_etag is True and the etags do
        not match or the resource's lock state is different from the expected
        state.
        """

    def copy(old_id, new_id):
        """Copy the resource old_id to new_id.

        Copy does not duplicate any write locks active on the source.

        raises CopyError if there was a problem with copying itself.
        raises KeyError if there is not resource with old_id
        """

    def move(old_id, new_id):
        """Move the resource with id `old_id` to `new_id`.

        A successful MOVE request on a write locked resource will not move the
        write lock with the resource.

        raises KeyError if there is no resource with old_id
        raises MoveError if there was a problem with moving itself.
        raises LockedByOtherSystemError if the resource is deleted by another user
        """

    def changeProperties(id, properties):
        """Change webdav properties of object.

        id: unique id
        properties: see IWebDAVProperties.properties
        """

    def lock(id, principal, until):
        """Lock resource for principal until a given datetime.

        A client MUST NOT submit the same write lock request twice.

        A successful request for an write lock results in the generation of a unique lock token
        associated with the requesting principal.

        A write locked null resource, referred to as a lock-null resource is possible.

        A write lock request is issued to a collection containing member URIs
        identifying resources that are currently locked in a manner which conflicts
        with the write lock, will fail.

        id: unique id
        until: datetime until the lock is valid.

        returns locktoken.
        raises KeyError if the resource could not be found
        raises LockingError if lock already exists for another principal
        """

    def unlock(id):
        """Unlock resource

        returns used locktoken, if the id of the resource does not exist, return none
        raises KeyError if the resource with id does not exist
        raises LockedByOtherSystemError if the resource is locked by another user
        """

    def _unlock(id, locktoken):
        """Unlock resource using the given locktoken. For tests."""

    def locked(id):
        """Return whether a resource is locked or not.

        returns tuple <lock owner>, <locked until>, <my lock>
            lock owner: principal id
            locked until: datetime.datetime instance
            my lock: True if the lock was issued by this system, False
                otherwise.

        returns None, None, None if the resource is not locked or is non-existant
        """

    def search(attributes, query):
        """Search for `query`

        returns an iterator of tuples containing the unique id and the values
        of the requested `attributes`:

            (unique_id, attributes[0], attributes[1], ...)
        """

    def search_sql(query):
        """Search for `query`

        query:
            SQL Select object obtained from IConnector.query()

        returns a list of IResource objects
        """

    def search_sql_count(query):
        """Count search results for `query`

        query:
            SQL Select object obtained from IConnector.query()

        returns integer
        """

    def query():
        """Not the most desirable API design, but functional for now

        returns query object for properties table for use with search_sql[_count]
        """


class ICachingConnector(IConnector):
    """A connector that caches."""

    def invalidate_cache(id):
        """Invalidate (and reload) the cache for the given id."""


class IWebDAVReadProperties(zope.interface.common.mapping.IEnumerableMapping):
    """Mapping for WebDAV properties.

    Keys are in the form (name, namespace), for example:

        {('resourcetype', 'DAV:'): 'article'}

    name, namespace and value should be unicode. If any is a str it must not
    contain non usascii characters.

    value can be the special value of DeleteProperty to indicate the property
    should be removed.
    """


class IWebDAVWriteProperties(zope.interface.common.mapping.IExtendedWriteMapping):
    """Write interface for WebDAVProperties."""


class IWebDAVProperties(IWebDAVReadProperties, IWebDAVWriteProperties):
    """Combined read and write interface for webdav properties."""


class CannonicalId(str):
    """A canonical id."""

    def __repr__(self):
        return '<CannonicalId %s>' % super().__repr__()


class IResource(zope.interface.Interface):
    """Represents a resource in the webdav.

    This is the resource interface the connector uses to return or get
    resources.
    """

    __name__ = zope.schema.TextLine(
        title='The name within the parent',
        description='Traverse the parent with this name to get the object.',
    )

    # TODO: make this an URI. We want the unique ids to not contain any unicode
    # characters, so a URI would be the right thing. Right now we have unicode
    # unique ids though makeing URI invalid.
    id = zope.interface.Attribute('Unique id of resource')

    type = zope.interface.Attribute(
        'Resource type (folder, image, ...). This is mapped to the property '
        'defined by `RESOURCE_TYPE_PROPERTY`'
    )

    data = zope.interface.Attribute('Resource main data (body, image data) as a file-like object.')

    is_collection = zope.schema.Bool()

    properties = zope.schema.Object(IWebDAVProperties, title='WebDAV properties')


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

    def sweep():
        """Minimize cache."""


class ICache(
    zope.interface.common.mapping.IReadMapping, zope.interface.common.mapping.IWriteMapping
):
    """Generic cache interface."""

    def keys(include_deleted=False):
        """Return the keys.

        If ``include_deleted`` is True entries marked as deleted are also
        returned.
        """

    def remove(key):
        """Really remove "key" from cache.

        __delitem__ marks an entry as deleted so the cache behaves as if it was
        deleted. ``remove`` really removes the entry.
        """


class IPersistentCache(ICache):
    """Cache that invaidates at server startup."""


class IPropertyCache(ICache):
    """A cache for properties."""


class IChildNameCache(ICache):
    """A cache for child names of collections."""


class IResourceInvalidatedEvent(zope.interface.Interface):
    """A resource has been invalidated."""

    id = zope.interface.Attribute('Unique id of resource')


@zope.interface.implementer(IResourceInvalidatedEvent)
class ResourceInvalidatedEvent:
    def __init__(self, id):
        self.id = id


class LockStatus(Enum):
    NONE = 0
    FOREIGN = 1
    OWN = 2
    TIMED_OUT = 3
