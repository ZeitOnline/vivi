# connector.py implementation of connector.py, based on
# gocept's functional sketch (connector.py)
# 2007-03-16 tomas
"""Connect to the CMS backend."""
#      RESOLVED: the id gets the standard prefix "http://xml.zeit.de/"

# NOTES, QUESTIONS
# [1]  Connector's __init__ has a named parameter <root> pointing to
#      the repository root URL (class-wide default provided for
#      compatibility to the stub, but I think parameter should be
#      mandatory).
# [2]  Exception for DAVNoCollectionError? Other exceptions?
# [3]  What is _make_id() supposed to do? Can we use url as id?
#      Is (given a connector's context) path and url interchangeable?
#      [RESOLVED] See [8]
# [3a] Even more so here. If we take the URL as id as seems to be the
#      current consensus (ugh!), what would mean to put a resource with
#      an id of "http://north.zeit.de/cms/foo/bar" into a repos rooted
#      at "http://south.zeit.de/cms2/"?
# [4]  See "Performance notes"
# [5]  Having a set of assorted strings as possible resource types
#      ('collection', 'article', 'centerpage', 'feed'...) looks horribly
#      naive.
# [6]  Check whether we need this. I don't quite understand
# [7]  Hrrgrr. davresource.py has create_file and create_collection methods.
#      We'll have to extend them to take attributes (transaction safety!)
# [7a] Where are the props on IResource?
# [8]  The id of a resource is its path counted from the repository's root.
#      For now, we assume it to be the same as the connector's root, which
#      is WRONG and should be fixed at some point.
#      RESOLVED: the id gets the standard prefix "http://xml.zeit.de/"
#      which may be overridden at Connector creation time.
# [9]  WebDAV can lock "non-existing" resources. To be more precise, it
#      locks URLs. This does make sense when trying to avoid race conditions
#      at resource creation.
#      But then we'll have to enhance davresource.py
#      [RESOLVED] Well. Partially. To wit:
#                 * "file" resources support, as of current mod_dav lock-null.
#                    We do use that in the case of file resources.
#                 * mod_dav behaves bizarrely with lock-null then mkcol.
#                    We do live with a "locking gap" when creating collections.
#                 Note that lock-null seems to be on its way to deprecation
#                 anyway. For me that means: avoid WebDAV for future projects.
# [10] we'll have to enhance it anyway because it doesn't support setting
#      lock expiry.
#      [RESOLVED]
# [11] Interface note: This implementation returns a lock token. The davclient
#      implementation keeps a cache of "the" lock token for "this" DAV resource,
#      but I fear our interface won't allow us to make use of that.
#      Maybe if we stick a davresource to each resource object... but then many
#      of the Connector methods would have to migrate to Resource anyway.
# [13] LockingError: we have many variants of that. List them, refine?
# [14] Here we try to decide whether to do a DAVCollection() or a DAVFile().
#      We should rather fix pydavclient's DAVResource() to return the
#      appropriate type (i.e. be an "abstract base class").
#      Or something equivalent, like doing away with the Collection/File difference
#      (which in my view would be more along WebDAV semantics)
# [16] which content-type?
# [17] Try to pass resource content around as IO object

import cStringIO
import datetime
import gocept.lxml.objectify
import httplib
import logging
import pytz
import re
import sys
import threading
import urlparse
import zeit.connector.cache
import zeit.connector.dav.davconnection
import zeit.connector.dav.davresource
import zeit.connector.interfaces
import zeit.connector.lockinfo
import zeit.connector.resource
import zeit.connector.search
import zope.cachedescriptors.property
import zope.interface


logger = logging.getLogger(__name__)

# The property holding the "resource type".
RESOURCE_TYPE_PROPERTY = zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY

# Highest possible datetime value. We use datetime-with-timezone everywhere.
# The MAXYEAR-1 is there to protect us from passing this bound when
# transforming into some local time
TIME_ETERNITY = datetime.datetime(
    datetime.MAXYEAR - 1, 12, 31, 23, 59, 59, 999999, tzinfo=pytz.UTC)


class DAVUnexpectedResultError(zeit.connector.dav.interfaces.DAVError):
    """Exception raised on unexpected HTTP return code.
    """
    pass

# id utilities
# IMPLEMENTATION NOTE
# Due to the way we implement IDs, we can "deduct" the ID of a
# resource's parent given the resource's ID (just chop off the
# last path's element). Some notes:
# - Resource ids all have a common prefix (default: http://xml.zeit.de/
#   Given the "correct" environment they might be interpreted as URL
# - Double slashes whithin the path part are treated as single ones (analog to POSIX).
# - Collection resources SHOULD end in slash, non-collections SHOULD NOT
#   (not sure whether we should enforce it, but we comply with it).

_max_timeout_days = ((sys.maxint-1) / 86400) - 1

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
    return max(d.days * 86400 + d.seconds + int(d.microseconds/1000000.0), 1)


class CannonicalId(unicode):
    """A canonical id."""

    def __repr__(self):
        return '<CannonicalId %s>' % super(CannonicalId, self).__repr__()


class Connector(object):
    """Connect to the CMS backend.
       WebDAV implementation based on pydavclient
    """

    zope.interface.implements(zeit.connector.interfaces.ICachingConnector)

    def __init__(self, roots={}, prefix=u'http://xml.zeit.de/'):
        # NOTE: roots['default'] should be defined
        self._roots = roots # "extra" roots, a dict. ATM only xroots['search']
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
        (scheme, netloc) = urlparse.urlsplit(url)[0:2]
        snetloc = "%s://%s" % (scheme, netloc)
        try: # grmblmmblpython
            host, port = netloc.split(':', 1)
            port = int(port)
        except ValueError:
            host, port = netloc, None
        # FIXME: Argh. DAVConnection should take schema as well!!!

        return zeit.connector.dav.davconnection.DAVConnection(host, port)

    def disconnect(self):
        connections = self.connections
        try:
            del connections.default
        except AttributeError:
            pass

    def listCollection(self, id):
        """List the filenames of a collection identified by <id> (see[8]). """
        __traceback_info__ = (id, )
        id = self._get_cannonical_id(id)
        property_cache = self.property_cache
        for child_id in self._get_resource_child_ids(id):
            if child_id in property_cache:
                yield (self._id_splitlast(child_id)[1].rstrip('/'), child_id)

    def _get_resource_type(self, id):
        __traceback_info__ = (id, )
        properties = self._get_resource_properties(id)
        r_type = properties.get(RESOURCE_TYPE_PROPERTY)
        if r_type is None:
            dav_type = properties.get(('resourcetype', 'DAV:'))
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
        __traceback_info__ = (id, )
        properties = None
        try:
            properties = self.property_cache[id]
        except KeyError:
            pass
        if properties is None:
            logger.debug("Getting properties from dav: %s" % id)
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
            response_id = self._loc2id(urlparse.urljoin(
                self._roots['default'], path))
            properties = response.get_all_properties()
            cached_properties = dict(cache.get(response_id, {}))
            cached_properties.pop(('cached-time', 'INTERNAL'), None)
            if cached_properties != properties:
                properties[('cached-time', 'INTERNAL')] = now
                cache[response_id] = properties

    def _update_child_id_cache(self, dav_response):
        if not dav_response.is_collection():
            return
        id = self._loc2id(urlparse.urljoin(self._roots['default'],
                                           dav_response.path))
        child_ids = self.child_name_cache[id] = [
            self._loc2id(urlparse.urljoin(self._roots['default'], path))
            for path in dav_response.get_child_names()]
        return child_ids

    def _get_resource_body(self, id):
        """Return body of resource."""
        __traceback_info__ = (id, )
        properties = self._get_resource_properties(id)
        data = None
        if properties.get(('getlastmodified', 'DAV:')):
            try:
                data = self.body_cache.getData(id, properties)
            except KeyError:
                logger.debug("Getting body from dav: %s" % id)
                response = self._get_dav_resource(id).get()
                data = self.body_cache.setData(id, properties, response)
                if not response.isclosed():
                    additional_data = response.read()
                    assert not additional_data, additional_data
        if data is None:
            # The resource does not have a body but only properties.
            data = cStringIO.StringIO('')
        return data

    def __getitem__(self, id):
        """Return the resource identified by `id`."""
        __traceback_info__ = (id, )
        id = self._get_cannonical_id(id)
        try:
            content_type = self._get_resource_properties(id).get(
                ('getcontenttype', 'DAV:'))
        except zeit.connector.dav.interfaces.DAVNotFoundError:
            raise KeyError("The resource %r does not exist." % unicode(id))
        return zeit.connector.resource.CachedResource(
            unicode(id), self._id_splitlast(id)[1].rstrip('/'),
            self._get_resource_type(id),
            lambda: self._get_resource_properties(id),
            lambda: self._get_resource_body(id),
            content_type=content_type)

    def __setitem__(self, id, object):
        """Add the given `object` to the document store under the given name.
        """
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
        self.get_connection().delete(self._id2loc(id), token)
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
        self._copy_or_move('copy', zeit.connector.interfaces.CopyError,
                           old_id, new_id)

    def move(self, old_id, new_id):
        """Move the resource with id `old_id` to `new_id`.
        """
        self._copy_or_move('move', zeit.connector.interfaces.MoveError,
                           old_id, new_id)

    def _copy_or_move(self, method_name, exception, old_id, new_id):
        source = self[old_id]  # Makes sure source exists.
        if self._is_descendant(new_id, old_id):
            raise exception(
                old_id,
                'Could not copy or move %s to a decendant of itself.' % old_id)

        logger.debug('copy: %s to %s' % (old_id, new_id))
        if self._get_cannonical_id(new_id) in self:
            raise exception(
                old_id,
                "Could not copy or move %s to %s, "
                "because target alread exists." % (
                    old_id, new_id))
        # Make old_id and new_id canonical. Use the canonical old_id to deduct
        # the canonical new_id:
        old_id = self._get_cannonical_id(old_id)
        if old_id.endswith('/'):
            if not new_id.endswith('/'):
                new_id += '/'
        else:
            if new_id.endswith('/'):
                new_id = new_id[:len(new_id)-1]
        old_loc = self._id2loc(old_id)
        new_loc = self._id2loc(new_id)

        conn = self.get_connection('default')
        method = getattr(conn, method_name)

        if old_id.endswith('/'):
           # We cannot copy/move folders directly because the properties of all
           # copied/moved objects lost then.
           self._add_collection(new_id)
           self.changeProperties(new_id, source.properties)
           for name, child_id in self.listCollection(old_id):
               self._copy_or_move(method_name, exception,
                                  child_id, urlparse.urljoin(new_id, name))
           if method_name == 'move':
               del self[old_id]
        else:
           response = method(old_loc, new_loc)

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
        path1 = urlparse.urlsplit(id1)[2].split('/')
        path2 = urlparse.urlsplit(id2)[2].split('/')
        return (len(path2) <= len(path1) and path2 == path1[:len(path2)])

    def changeProperties(self, id, properties, locktoken=None):
        id = self._get_cannonical_id(id)
        if locktoken is None:
            locktoken = self._get_my_locktoken(id)
        davres = self._get_dav_resource(id)
        properties = dict(properties)
        properties[('cached-time', 'INTERNAL')] = (
            zeit.connector.interfaces.DeleteProperty)
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        davres.change_properties(
            properties,
            delmark=zeit.connector.interfaces.DeleteProperty,
            locktoken=locktoken)

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
            token = self.get_connection().lock(url,
                                               owner=principal,
                                               depth=0,
                                               timeout=_abs2timeout(until))
        except zeit.connector.dav.interfaces.DAVLockedError:
            raise zeit.connector.interfaces.LockingError(
                id, "%s is already locked." % id)
        # Just pass-on other exceptions. It's more informative

        if token:
            self._put_my_lockinfo(id, token, principal, until)
        self._invalidate_cache(id)
        return token

    def unlock(self, id, locktoken=None, invalidate=True):
        if invalidate:
            self._invalidate_cache(id)
        url = self._id2loc(self._get_cannonical_id(id))
        locktoken = locktoken or self._get_dav_lock(id).get('locktoken')
        if locktoken:
            try:
                self.get_connection().unlock(url, locktoken)
            finally:
                if invalidate:
                    self._put_my_lockinfo(id, None)
        if invalidate:
            self._invalidate_cache(id)
        return locktoken

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

        mylock = self._get_my_lockinfo(id)
        if mylock is None and davlock and owner:
            # We have no information about the lock. Let's see if the principal
            # is one we know. It's most likely that it actually was our lock
            # but we just forgot about it.
            authentication = zope.component.queryUtility(
                zope.authentication.interfaces.IAuthentication)
            if authentication is not None:
                try:
                    authentication.getPrincipal(owner)
                except zope.authentication.interfaces.PrincipalLookupError:
                    pass
                else:
                    mylock = (token, owner, timeout)
                    self._put_my_lockinfo(id, *mylock)
        elif mylock and mylock[0] != token:
            # We know something about a locktoken, but it is no longer valid.
            # Forget about it.
            self._put_my_lockinfo(id, None)
            mylock = None

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

        logger.debug('Searching for %s' % (expr._render(),))
        conn = self.get_connection('search')

        davres = zeit.connector.dav.davresource.DAVResult(
               conn.search(self._roots.get('search', self._roots['default']),
                            body=expr._render()))
        for url, resp in davres.responses.items():
            try:
                id = self._loc2id(urlparse.urljoin(self._roots['default'], url))
            except ValueError:
                # Search returns documents which are outside the root, ignore
                continue
            props = resp.get_all_properties()
            yield tuple([id] + [props[(a.name, a.namespace)] for a in attrlist])

    def _get_my_lockinfo(self, id):
        # returns (token, principal, time)
        return self.locktokens.get(id)

    def _put_my_lockinfo(self, id, token, principal=None, time=None):
        # FIXME better defaults
        if token is None:
            self.locktokens.remove(id)
        else:
            self.locktokens.set(id, (token, principal, time))

    def _get_my_locktoken(self, id):
        locker, until, myself = self.locked(id)

        if (locker or until) and not myself:
            __traceback_info__ = (id, locker, until)
            raise zeit.connector.interfaces.LockedByOtherSystemError(
                id, locker, until)
        my_lock_info = self._get_my_lockinfo(id)
        if my_lock_info:
            return my_lock_info[0]
        return None

    def _id2loc(self, id):
        """Transform an id to a location, e.g.
             http://xml.zeit.de/2006/12/ -->
             http://zip4.zeit.de:9999/cms/work/2006/12/
           Just a textual transformation: replace _prefix with _root"""
        if not id.startswith(self._prefix):
            raise ValueError("Bad id %r (prefix is %r)" % (id, self._prefix))
        path = id[len(self._prefix):]
        #if isinstance(path, unicode):
        #    path = path.encode('utf8')
        #path = urllib.quote(path)
        return self._roots['default'] + path

    def _loc2id(self, loc):
        """Transform a location to an id, e.g.
             http://zip4.zeit.de:9999/cms/work/2006/12/ -->
             http://xml.zeit.de/2006/12/
           Just a textual transformation: replace _root with _prefix"""
        root = self._roots['default']
        if not loc.startswith(root):
            raise ValueError("Bad location %r (root is %r)" % (loc, root))
        path = loc[len(root):]
        #path = unicode(urllib.unquote(path), 'utf8')
        return self._prefix + path

    def _internal_add(self, id, resource, verify_etag=True):
        """The grunt work of __setitem__() and add()
        """
        self._invalidate_cache(id)
        locktoken = self._get_my_locktoken(id) #  FIXME [7] [16]
        autolock = (locktoken is None)
        iscoll = (resource.type == 'collection'
                  or resource.contentType == 'httpd/unix-directory')
        if iscoll and not id.endswith('/'):
            id = id + '/'

        if iscoll:
            # It is not necessary (and not possible) to lock collections when
            # they don't exist because MKCOL does *not* overwrite anything. So
            # only lock for files
            if not self._check_dav_resource(id):
                self._add_collection(id)
            davres = self._get_dav_resource(id, ensure='collection')

        if autolock:
            locktoken = self.lock(id, "AUTOLOCK",
                                  datetime.datetime.now(pytz.UTC) +
                                  datetime.timedelta(seconds=60))
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
                uuid = resource.properties.get(
                    zeit.connector.interfaces.UUID_PROPERTY)
                if uuid:
                    headers['Zeit-DocID'] = uuid

                try:
                    conn.put(self._id2loc(id), data,
                             mime_type=resource.contentType,
                             locktoken=locktoken, etag=etag,
                             extra_headers=headers)
                except zeit.connector.dav.interfaces.PreconditionFailedError:
                    if self[id].data.read() != data:
                        raise

            # Set the resource type from resource.type.
            properties = dict(resource.properties)
            properties[RESOURCE_TYPE_PROPERTY] = resource.type
            __traceback_info__ = (
                dict(properties), zeit.connector.interfaces.DeleteProperty)
            self.changeProperties(id, properties, locktoken=locktoken)
        finally:
            if autolock and locktoken:  # This was _our_ lock. Cleanup:

                self.unlock(id, locktoken=locktoken)
            else:
                self._invalidate_cache(id)

    def _add_collection(self, id):
        # NOTE id is the collection's id. Trailing slash is appended as necessary.
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
           (Actually return the ETag, but don't rely on that yet)
        """
        url = self._id2loc(id)
        hresp = zeit.connector.dav.davresource.DAVResource(
            url, conn=self.get_connection()).head()
        if not hresp:
            return None # FIXME throw exception?
        hresp.read()
        st = int(hresp.status)
        if  st== httplib.OK:
            return hresp.getheader('ETag', 'Unspecified ETag')
        elif st == httplib.NOT_FOUND:
            return None
        else:
            raise DAVUnexpectedResultError(
                'Unexpected result code for %s: %d' % (url, st))

    def _get_dav_resource(self, id, ensure=None):
        """returns resource corresponding to <id>, which see [8],
        <ensure> may be 'file' or 'collection'"""
        # FIXME [14] Make DAVResource() return appropriate sub-type
        url = self._id2loc(id)
        # FIXME here, we tacitly assume that URIs ending with '/' MUST
        # be collections. This ain't strictly right
        wantcoll = (ensure == 'collection' or url.endswith('/'))
        if wantcoll:
            klass = res = zeit.connector.dav.davresource.DAVCollection
        elif ensure == 'file':
            klass = zeit.connector.dav.davresource.DAVFile
        else:
            # This one to disappear when [14] fixed
            klass = zeit.connector.dav.davresource.DAVResource
        return klass(url, conn=self.get_connection())

    def _get_dav_lock(self, id):
        lockdiscovery = self[id].properties[('lockdiscovery', 'DAV:')]

        if not lockdiscovery:
            return {}

        lock_info = gocept.lxml.objectify.fromstring(lockdiscovery)
        davlock = {}

        try:
            lockinfo_node = lock_info.activelock
        except AttributeError:
            pass
        else:
            try:
                davlock['owner'] = unicode(lockinfo_node['{DAV:}owner'])
            except AttributeError:
                davlock['owner'] = None
            # We get timeout in "Second-1337" format. Extract, add to ref time
            timeout = lockinfo_node.timeout
            if not timeout:
                timeout = None
            elif timeout == 'Infinity':
                timeout = TIME_ETERNITY
            else:
                m = re.match("second-(\d+)", unicode(timeout), re.I)
                if m is None:
                    # Better too much than not enough
                    timeout = TIME_ETERNITY
                else:
                    reftime = self[id].properties.get(
                        ('cached-time', 'INTERNAL'))
                    if not isinstance(reftime, datetime.datetime):
                        # XXX untested
                        reftime = datetime.datetime.now(pytz.UTC)
                    timeout = reftime + datetime.timedelta(
                        seconds=int(m.group(1)))
                davlock['timeout'] = timeout

            davlock['locktoken'] = unicode(lockinfo_node.locktoken.href)
        return davlock

    @staticmethod
    def _remove_from_caches(id, caches):
        for cache in caches:
            try:
                del cache[id]
            except KeyError:
                logger.debug("%s not in %s" % (id, cache))

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
        except zeit.connector.dav.interfaces.DAVRedirectError, e:
            exists = False
            new_location = e.response.getheader('location')
            if new_location:
                self._invalidate_cache(self._loc2id(new_location))
        else:
            exists = True
        if exists:
            self._update_property_cache(davres)
            self._update_child_id_cache(davres)
        else:
            self._remove_from_caches(id, [self.property_cache,
                                          self.child_name_cache])
        parent, name = self._id_splitlast(id)
        try:
            children = self.child_name_cache[parent]
        except KeyError:
            # We don't know the parent's child ids. Be sure we don't know the
            # parent's properties eitehr
            self._remove_from_caches(parent, [self.property_cache])
        else:
            if exists and id not in children:
                children.insert(unicode(id))
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
            self._id2loc(id), conn=self.get_connection())
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

    @zope.cachedescriptors.property.Lazy
    def locktokens(self):
        return zeit.connector.lockinfo.LockInfo()
