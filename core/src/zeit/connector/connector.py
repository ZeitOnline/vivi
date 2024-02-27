"""Connect to the CMS backend."""

from io import BytesIO
import datetime
import http.client
import logging
import re
import sys
import threading
import urllib.parse

import gocept.cache.property
import lxml.etree
import pytz
import zope.cachedescriptors.property
import zope.interface

from zeit.connector.interfaces import ID_NAMESPACE
import zeit.connector.cache
import zeit.connector.dav.davconnection
import zeit.connector.dav.davresource
import zeit.connector.interfaces
import zeit.connector.resource
import zeit.connector.search


# IMPLEMENTATION NOTES:
#
# - Due to the way we implement IDs, we can "deduct" the ID of a
#   resource's parent given the resource's ID (just chop off the
#   last path's element).
#
# - Resource ids all have a common prefix (default: http://xml.zeit.de/)
#   Given the "correct" environment they might be interpreted as URL.
#
# - Double slashes whithin the path part are treated as single ones (analog
#   to POSIX).
#
# - Collection resources SHOULD end in slash, non-collections SHOULD NOT
#   (not sure whether we should enforce it, but we comply with it).


logger = logging.getLogger(__name__)

# The property holding the "resource type".
RESOURCE_TYPE_PROPERTY = zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY


# Highest possible datetime value. We use datetime-with-timezone everywhere.
# The MAXYEAR-1 is there to protect us from passing this bound when
# transforming into some local time
TIME_ETERNITY = datetime.datetime(datetime.MAXYEAR - 1, 12, 31, 23, 59, 59, 999999, tzinfo=pytz.UTC)


class DAVUnexpectedResultError(zeit.connector.dav.interfaces.DAVError):
    """Exception raised on unexpected HTTP return code."""


_max_timeout_days = ((sys.maxsize - 1) / 86400) - 1


def _abs2timeout(time):
    # Convert timedelta to int (seconds). Return None when (near) overflow
    # which means infinte.
    # Ain't there anything similar in Python? Grr.
    if time is None:
        return None
    d = time - datetime.datetime.now(pytz.UTC)
    if abs(d.days) > _max_timeout_days:
        return None
    # No negative or zero timeouts:
    return max(d.days * 86400 + d.seconds + int(d.microseconds / 1000000.0), 1)


class CannonicalId(str):
    """A canonical id."""

    def __repr__(self):
        return '<CannonicalId %s>' % super().__repr__()


@zope.interface.implementer(zeit.connector.interfaces.ICachingConnector)
class Connector:
    """Connect to the CMS backend.
    WebDAV implementation based on pydavclient
    """

    long_name = 'DAV connector'

    def __init__(self, roots=None, prefix='http://xml.zeit.de/'):
        # NOTE: roots['default'] should be defined
        # "extra" roots, a dict. ATM only xroots['search']
        if roots is None:
            roots = {}
        self._roots = roots
        self._prefix = prefix
        self.connections = threading.local()

    def get_connection(self, root='default'):
        """Try to get a cached connection suitable for url"""
        try:
            connection = getattr(self.connections, root)
        except AttributeError:
            connection = self.create_connection(root)
            setattr(self.connections, root, connection)
        return connection

    def create_connection(self, root):
        """Create a new connection."""
        logger.debug('New connection')
        url = self._roots[root]
        (scheme, netloc) = urllib.parse.urlsplit(url)[0:2]
        try:  # grmblmmblpython
            host, port = netloc.split(':', 1)
            port = int(port)
        except ValueError:
            host, port = netloc, None
        # FIXME: DAVConnection should take schema as well. There is no HTTPS
        # supported like this:
        return zeit.connector.dav.davconnection.DAVConnection(host, port)

    def disconnect(self):
        for root in self._roots:
            conn = getattr(self.connections, root, None)
            if conn is None:
                continue
            conn.close()
            delattr(self.connections, root)

    def listCollection(self, id):
        """List the filenames of a collection identified by <id> (see[8])."""
        __traceback_info__ = (id,)
        id = self._get_cannonical_id(id)
        for child_id in self._get_resource_child_ids(id):
            yield (self._id_splitlast(child_id)[1].rstrip('/'), child_id)

    def _get_resource_type(self, id):
        __traceback_info__ = (id,)
        properties = self._get_resource_properties(id)
        r_type = properties.get(RESOURCE_TYPE_PROPERTY)
        if r_type is None:
            dav_type = properties.get(('resourcetype', 'DAV:'), '')
            content_type = properties.get(('getcontenttype', 'DAV:'), '')
            __traceback_info__ = (id, dav_type, content_type)
            if dav_type and 'collection' in dav_type:
                r_type = 'collection'
            elif content_type.startswith('image/'):
                r_type = 'image'
            else:
                r_type = 'unknown'
        return r_type

    def _get_resource_properties(self, id):
        __traceback_info__ = (id,)
        properties = None
        try:
            properties = self.property_cache[id]
        except KeyError:
            pass
        if properties is None:
            logger.debug('Getting properties from dav: %s' % id)
            davres = self._get_dav_resource(id)
            if davres._result is None:
                davres.update()
            self._update_property_cache(davres)
            self._update_child_id_cache(davres)
            properties = davres.get_all_properties()
        return properties

    def _get_resource_child_ids(self, id):
        try:
            child_ids = self.child_name_cache[id]
        except KeyError:
            davres = self._get_dav_resource(id)
            if davres._result is None:
                davres.update()
            self._update_property_cache(davres)
            child_ids = self._update_child_id_cache(davres)
        return child_ids

    def _update_property_cache(self, dav_result):
        now = datetime.datetime.now(pytz.UTC)
        cache = self.property_cache
        for path, response in dav_result._result.responses.items():
            # response_id will be the canonical id, i.e. collections end with a
            # slash (/)
            response_id = self._loc2id(urllib.parse.urljoin(self._roots['default'], path))
            properties = response.get_all_properties()
            cached_properties = dict(cache.get(response_id, {}))
            cached_properties.pop(('cached-time', 'INTERNAL'), None)
            if cached_properties != properties:
                properties[('cached-time', 'INTERNAL')] = now
                cache[response_id] = properties

    def _update_child_id_cache(self, dav_response):
        if not dav_response.is_collection():
            return None
        id = self._loc2id(urllib.parse.urljoin(self._roots['default'], dav_response.path))
        child_ids = self.child_name_cache[id] = [
            self._loc2id(urllib.parse.urljoin(self._roots['default'], path))
            for path in dav_response.get_child_names()
        ]
        return child_ids

    def _get_resource_body(self, id):
        """Return body of resource."""
        __traceback_info__ = (id,)
        properties = self._get_resource_properties(id)
        data = None
        if properties.get(('getlastmodified', 'DAV:')):
            try:
                data = self.body_cache.getData(id, properties)
            except KeyError:
                logger.debug('Getting body from dav: %s' % id)
                response = self._get_dav_resource(id).get()
                data = self.body_cache.setData(id, properties, response)
                if not response.isclosed():
                    additional_data = response.read()
                    assert not additional_data, additional_data
        if data is None:
            # The resource does not have a body but only properties.
            data = BytesIO(b'')
        return data

    def __getitem__(self, id):
        """Return the resource identified by `id`."""
        __traceback_info__ = (id,)
        id = self._get_cannonical_id(id)
        try:
            content_type = self._get_resource_properties(id).get(('getcontenttype', 'DAV:'))
        except (
            zeit.connector.dav.interfaces.DAVNotFoundError,
            zeit.connector.dav.interfaces.DAVBadRequestError,
        ):
            raise KeyError('The resource %r does not exist.' % str(id))
        return zeit.connector.resource.CachedResource(
            str(id),
            self._id_splitlast(id)[1].rstrip('/'),
            self._get_resource_type(id),
            lambda: self._get_resource_properties(id),
            lambda: self._get_resource_body(id),
            contentType=content_type,
        )

    def __setitem__(self, id, object):
        """Add the given `object` to the document store under the given name."""
        id = self._get_cannonical_id(id)
        resource = zeit.connector.interfaces.IResource(object)
        resource.id = id  # override
        self._internal_add(id, resource)

    def __delitem__(self, id):
        """Remove the resource from the repository."""
        id = self._get_cannonical_id(id)

        # Invalidate the cache to make sure we have the real lock information
        self._invalidate_cache(id)
        token = self._get_my_locktoken(id)  # raises LockedByOtherSystemError
        try:
            self.get_connection().delete(self._id2loc(id), token)
        except zeit.connector.dav.interfaces.DAVNotFoundError:
            raise KeyError(id)
        self._invalidate_cache(id)

    def __contains__(self, id):
        # Because we cache a lot it will be ok to just grab the object:
        try:
            self[id]
        except KeyError:
            return False
        return True

    def add(self, object, verify_etag=True):
        resource = zeit.connector.interfaces.IResource(object)
        id = self._get_cannonical_id(resource.id)
        self._internal_add(id, resource, verify_etag)

    def copy(self, old_id, new_id):
        """Copy the resource old_id to new_id."""
        self._copy_or_move('copy', zeit.connector.interfaces.CopyError, old_id, new_id)

    def move(self, old_id, new_id):
        """Move the resource with id `old_id` to `new_id`."""
        self._copy_or_move(
            'move', zeit.connector.interfaces.MoveError, old_id, new_id, resolve_conflicts=True
        )

    def _copy_or_move(self, method_name, exception, old_id, new_id, resolve_conflicts=False):
        source = self[old_id]  # Makes sure source exists.
        if self._is_descendant(new_id, old_id):
            raise exception(old_id, 'Could not copy or move %s to a decendant of itself.' % old_id)

        logger.debug('copy: %s to %s' % (old_id, new_id))
        if self._get_cannonical_id(new_id) in self:
            target = self[new_id]
            # The target already exists. It's possible that there was a
            # conflict. For non-directories verify body.
            if not (
                resolve_conflicts
                and 'httpd/unix-directory' not in (source.contentType, target.contentType)
                and source.data.read() == self[new_id].data.read()
            ):
                raise exception(
                    old_id,
                    'Could not copy or move %s to %s, '
                    'because target alread exists.' % (old_id, new_id),
                )
        # Make old_id and new_id canonical. Use the canonical old_id to deduct
        # the canonical new_id:
        old_id = self._get_cannonical_id(old_id)
        if old_id.endswith('/'):
            if not new_id.endswith('/'):
                new_id += '/'
        else:
            if new_id.endswith('/'):
                new_id = new_id[: len(new_id) - 1]
        old_loc = self._id2loc(old_id)
        new_loc = self._id2loc(new_id)

        conn = self.get_connection('default')
        method = getattr(conn, method_name)

        if old_id.endswith('/'):
            # We cannot copy/move folders directly because the properties of
            # all copied/moved objects lost then.
            self._add_collection(new_id)
            self.changeProperties(new_id, source.properties)
            for name, child_id in self.listCollection(old_id):
                self._copy_or_move(
                    method_name, exception, child_id, urllib.parse.urljoin(new_id, name)
                )
            if method_name == 'move':
                del self[old_id]
        else:
            token = self._get_my_locktoken(old_id)
            method(old_loc, new_loc, locktoken=token)

        self._invalidate_cache(old_id)
        self._invalidate_cache(new_id)

    @staticmethod
    def _is_descendant(id1, id2):
        """Return if id1 is descandant of id2.

        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b/c/d/e')
        False
        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b')
        True
        >>> Connector._is_descendant('http://foo.bar/a/b/c',
        ...                          'http://foo.bar/a/b/d')
        False
        """
        path1 = urllib.parse.urlsplit(id1)[2].split('/')
        path2 = urllib.parse.urlsplit(id2)[2].split('/')
        return len(path2) <= len(path1) and path2 == path1[: len(path2)]

    def changeProperties(self, id, properties, locktoken=None):
        id = self._get_cannonical_id(id)
        if locktoken is None:
            locktoken = self._get_my_locktoken(id)
        davres = self._get_dav_resource(id)
        properties = dict(properties)
        properties[('cached-time', 'INTERNAL')] = zeit.connector.interfaces.DeleteProperty
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        davres.change_properties(
            properties, delmark=zeit.connector.interfaces.DeleteProperty, locktoken=locktoken
        )

        # Update property cache
        del properties[('cached-time', 'INTERNAL')]
        try:
            cached_properties = self.property_cache[id]
        except KeyError:
            pass
        else:
            cached_properties.update(properties)
            self.property_cache[id] = cached_properties

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        url = self._id2loc(self._get_cannonical_id(id))
        token = None
        try:
            # NOTE: _timeout() returns None for timeouts too long. This blends
            #       with DAVConnection, which converts None to 'Infinite'.
            token = self.get_connection().lock(
                url, owner=principal, depth=0, timeout=_abs2timeout(until)
            )
        except zeit.connector.dav.interfaces.DAVLockedError:
            raise zeit.connector.interfaces.LockingError(id, '%s is already locked.' % id)
        # Just pass-on other exceptions. It's more informative

        self._invalidate_cache(id)
        return token

    def unlock(self, id, locktoken=None, invalidate=True):
        if invalidate:
            self._invalidate_cache(id)
        url = self._id2loc(self._get_cannonical_id(id))
        locktoken = locktoken or self._get_dav_lock(id).get('locktoken')
        if locktoken:
            self.get_connection().unlock(url, locktoken)
        if invalidate:
            self._invalidate_cache(id)

    def locked(self, id):
        id = self._get_cannonical_id(id)
        try:
            davlock = self._get_dav_lock(id)
        except KeyError:
            # The resource does not exist on the server. This means it *cannot*
            # be locked.
            davlock = {}
        owner = davlock.get('owner')
        timeout = davlock.get('timeout')
        token = davlock.get('locktoken')
        mylock = None

        if davlock and owner:
            # Let's see if the principal is one we know.
            try:
                import zope.authentication.interfaces  # UI-only dependency

                authentication = zope.component.queryUtility(
                    zope.authentication.interfaces.IAuthentication
                )
            except ImportError:
                authentication = None
            if authentication is not None:
                try:
                    authentication.getPrincipal(owner)
                except zope.authentication.interfaces.PrincipalLookupError:
                    pass
                else:
                    mylock = (token, owner, timeout)

        if timeout == 'Infinite':
            timeout = TIME_ETERNITY
        if timeout and timeout < datetime.datetime.now(pytz.UTC):
            # The lock has timed out
            self._invalidate_cache(id)
            return self.locked(id)

        return (owner, timeout, mylock is not None)

    def search(self, attrlist, expr):
        """Search repository behind this connector according to <expr>.
        For each match return the values of the attributes
        specified in attrlist
        """
        # Collect "result" vars as bindings "into" expression:
        for at in attrlist:
            expr = at.bind(zeit.connector.search.SearchSymbol('_')) & expr
        expr = expr._render()

        logger.debug('Searching for %s' % expr)
        if isinstance(expr, str):
            expr = expr.encode('utf8')
        conn = self.get_connection('search')
        response = conn.search(self._roots.get('search', self._roots['default']), body=expr)
        davres = zeit.connector.dav.davresource.DAVResult(response)
        if davres.has_errors():
            raise zeit.connector.dav.interfaces.DAVError(
                davres.status, davres.reason, '/', davres.body, response
            )
        for url, resp in davres.responses.items():
            try:
                id = self._loc2id(urllib.parse.urljoin(self._roots['default'], url))
            except ValueError:
                # Search returns documents which are outside the root, ignore
                continue
            props = resp.get_all_properties()
            yield tuple([id] + [props[(a.name, a.namespace)] for a in attrlist])

    def _get_my_locktoken(self, id):
        locker, until, myself = self.locked(id)

        if (locker or until) and not myself:
            __traceback_info__ = (id, locker, until)
            raise zeit.connector.interfaces.LockedByOtherSystemError(id, locker, until)
        try:
            davlock = self._get_dav_lock(id)
        except KeyError:
            davlock = {}
        return davlock.get('locktoken')

    def _id2loc(self, id):
        """Transform an id to a location, e.g.
          http://xml.zeit.de/2006/12/ -->
          http://zip4.zeit.de:9999/cms/work/2006/12/
        Just a textual transformation: replace _prefix with _root"""
        if not id.startswith(self._prefix):
            raise ValueError('Bad id %r (prefix is %r)' % (id, self._prefix))
        path = id[len(self._prefix) :]
        return self._roots['default'] + path

    def _loc2id(self, loc):
        """Transform a location to an id, e.g.
          http://zip4.zeit.de:9999/cms/work/2006/12/ -->
          http://xml.zeit.de/2006/12/
        Just a textual transformation: replace _root with _prefix"""
        root = self._roots['default']
        if not loc.startswith(root):
            raise ValueError('Bad location %r (root is %r)' % (loc, root))
        path = loc[len(root) :]
        return self._prefix + path

    def _internal_add(self, id, resource, verify_etag=True):
        """The grunt work of __setitem__() and add()"""
        if id.rstrip('/') == ID_NAMESPACE.rstrip('/'):
            raise KeyError('Cannot write to root object')
        self._invalidate_cache(id)
        locktoken = self._get_my_locktoken(id)
        autolock = locktoken is None
        iscoll = resource.type == 'collection' or resource.contentType == 'httpd/unix-directory'
        if iscoll and not id.endswith('/'):
            id = id + '/'

        if iscoll:
            # It is not necessary (and not possible) to lock collections when
            # they don't exist because MKCOL does *not* overwrite anything. So
            # only lock for files
            if not self._check_dav_resource(id):
                self._add_collection(id)

        if autolock:
            locktoken = self.lock(
                id, 'AUTOLOCK', datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=60)
            )
        try:
            if not iscoll:  # We are a file resource:
                if hasattr(resource.data, 'seek'):
                    resource.data.seek(0)
                # We should pass the data as IO object. This is not supported
                # out of the box by httplib (which is used in DAV). We could
                # override the send method though.
                data = resource.data.read()
                etag = None
                if verify_etag:
                    etag = resource.properties.get(('getetag', 'DAV:'))
                conn = self.get_connection()

                headers = {}
                uuid = resource.properties.get(zeit.connector.interfaces.UUID_PROPERTY)
                if uuid:
                    headers['Zeit-DocID'] = uuid

                try:
                    conn.put(
                        self._id2loc(id),
                        data,
                        mime_type=resource.contentType,
                        locktoken=locktoken,
                        etag=etag,
                        extra_headers=headers,
                    )
                except zeit.connector.dav.interfaces.PreconditionFailedError:
                    if self[id].data.read() != data:
                        raise

            # Set the resource type from resource.type.
            properties = dict(resource.properties)
            properties[RESOURCE_TYPE_PROPERTY] = resource.type
            __traceback_info__ = (dict(properties),)
            self.changeProperties(id, properties, locktoken=locktoken)
        finally:
            if autolock and locktoken:  # This was _our_ lock. Cleanup:
                self.unlock(id, locktoken=locktoken)
            else:
                self._invalidate_cache(id)

    def _add_collection(self, id):
        # NOTE id is the collection's id. Trailing slash is appended if needed.
        # We assume id to map to a non-existent resource, its
        # parent is assumed to exist.
        if not id.endswith('/'):
            id += '/'
        conn = self.get_connection()
        url = self._id2loc(id)
        return conn.mkcol(url)

    def _check_dav_resource(self, id):
        """Check whether resource <id> exists.
        Issue a head request and return not None when found.
        """
        url = self._id2loc(id)
        hresp = zeit.connector.dav.davresource.DAVResource(url, conn=self.get_connection()).head()
        if not hresp:
            return False
        hresp.read()
        st = int(hresp.status)
        if st == http.client.OK:
            return True
        elif st == http.client.NOT_FOUND:
            return False
        else:
            raise DAVUnexpectedResultError('Unexpected result code for %s: %d' % (url, st))

    def _get_dav_resource(self, id):
        """returns resource corresponding to <id>"""
        url = self._id2loc(id)
        # NOTE: We tacitly assume that URIs ending with '/' MUST
        # be collections. This ain't strictly right, but is sufficient.
        if url.endswith('/'):
            klass = zeit.connector.dav.davresource.DAVCollection
        else:
            klass = zeit.connector.dav.davresource.DAVResource
        return klass(url, conn=self.get_connection())

    def _get_dav_lock(self, id):
        lockdiscovery = self[id].properties[('lockdiscovery', 'DAV:')]

        if not lockdiscovery:
            return {}

        lock_info = lxml.etree.fromstring(lockdiscovery)
        lockinfo_node = lock_info.find('{DAV:}activelock')
        if lockinfo_node is None:
            return {}

        davlock = {}
        owner = lockinfo_node.find('{DAV:}owner')
        davlock['owner'] = owner.text if owner is not None else None
        # We get timeout in "Second-1337" format. Extract, add to ref time
        timeout = getattr(lockinfo_node.find('{DAV:}timeout'), 'text', None)
        if not timeout:
            timeout = None
        elif timeout == 'Infinity':
            timeout = TIME_ETERNITY
        else:
            m = re.match(r'second-(\d+)', timeout, re.I)
            if m is None:
                # Better too much than not enough
                timeout = TIME_ETERNITY
            else:
                reftime = self[id].properties.get(('cached-time', 'INTERNAL'))
                if not isinstance(reftime, datetime.datetime):
                    # XXX untested
                    reftime = datetime.datetime.now(pytz.UTC)
                timeout = reftime + datetime.timedelta(seconds=int(m.group(1)))
            davlock['timeout'] = timeout

        davlock['locktoken'] = lockinfo_node.find('{DAV:}locktoken/{DAV:}href').text
        return davlock

    @staticmethod
    def _remove_from_caches(id, caches):
        for cache in caches:
            try:
                del cache[id]
            except KeyError:
                logger.debug('%s not in %s' % (id, cache))

    def _invalidate_cache(self, id):
        # Make an indirection here to allow zopeconnector to use events.
        self.invalidate_cache(id)

    def invalidate_cache(self, id):
        """invalidate cache (and refill)."""
        try:
            # Loads properties from dav and stores when necessary.
            davres = self._get_dav_resource(id)
            if davres._result is None:
                davres.update(depth=1)
        except zeit.connector.dav.interfaces.DAVNotFoundError:
            exists = False
        except zeit.connector.dav.interfaces.DAVRedirectError as e:
            exists = False
            new_location = e.response.getheader('location')
            if new_location:
                self._invalidate_cache(self._loc2id(new_location))
        else:
            exists = True

        if exists:
            self._update_property_cache(davres)
            self._update_child_id_cache(davres)

            # Remove no longer existing child entries from property_cache
            IPersistentCache = zeit.connector.interfaces.IPersistentCache
            if id.endswith('/') and IPersistentCache.providedBy(self.property_cache):
                end = id[:-1] + chr(ord('/') + 1)
                for key in self.property_cache.keys(min=id, max=end):
                    if key not in self.child_name_cache:
                        del self.property_cache[key]
        else:
            self._remove_from_caches(id, [self.property_cache, self.child_name_cache])

        # Update our parent's child_name_cache
        parent, name = self._id_splitlast(id)
        try:
            children = self.child_name_cache[parent]
        except KeyError:
            # We don't know the parent's child ids. Be sure we don't know the
            # parent's properties eitehr
            self._remove_from_caches(parent, [self.property_cache])
        else:
            if exists and id not in children:
                children.insert(str(id))
            elif not exists and id in children:
                children.remove(id)
            try:
                davres = self._get_dav_resource(parent)
                if davres._result is None:
                    davres.update(depth=0)
            except zeit.connector.dav.interfaces.DAVNotFoundError:
                # Apparently the parent dissapeared somehow.
                self._invalidate_cache(parent)
            else:
                self._update_property_cache(davres)

    def _get_cannonical_id(self, id):
        """Add / for collections if not appended yet."""
        if isinstance(id, CannonicalId):
            return id
        if id == self._prefix:
            return CannonicalId(id)
        if id.endswith('/'):
            id = id[:-1]
        if self.property_cache.get(id + '/') is not None:
            return CannonicalId(id + '/')
        if self.property_cache.get(id) is not None:
            return CannonicalId(id)
        dav_resource = zeit.connector.dav.davresource.DAVResource(
            self._id2loc(id), conn=self.get_connection()
        )
        response = dav_resource.head()
        response.read()
        if response.status == 301:
            return CannonicalId(id + '/')
        return CannonicalId(id)

    @staticmethod
    def _id_splitlast(id):
        # Split id in parent/name parts
        # FIXME fix borderline cases: _splitlast(""), _splitlast("/")
        parent, last = id.rstrip('/').rsplit('/', 1)
        if id.endswith('/'):
            last = last + '/'
        return parent + '/', last

    @zope.cachedescriptors.property.Lazy
    def body_cache(self):
        return zeit.connector.cache.ResourceCache()

    @zope.cachedescriptors.property.Lazy
    def property_cache(self):
        return zeit.connector.cache.PropertyCache()

    @zope.cachedescriptors.property.Lazy
    def child_name_cache(self):
        return zeit.connector.cache.ChildNameCache()

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product

        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector')
        return cls({'default': config['document-store'], 'search': config['document-store-search']})


factory = Connector.factory  # zope.dottedname does not support classmethods


class TransactionBoundCachingConnector(Connector):
    long_name = '(Transaction-bound) DAV connector'

    body_cache = gocept.cache.property.TransactionBoundCache(
        '_v_body_cache', zeit.connector.cache.ResourceCache
    )

    property_cache = gocept.cache.property.TransactionBoundCache(
        '_v_property_cache', zeit.connector.cache.PropertyCache
    )

    child_name_cache = gocept.cache.property.TransactionBoundCache(
        '_v_child_name_cache', zeit.connector.cache.ChildNameCache
    )


tbc_factory = TransactionBoundCachingConnector.factory
