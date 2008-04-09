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

import StringIO
import datetime
import httplib
import logging
import os
import random
import re
import sys
import time
import urlparse

import pytz
import gocept.lxml.objectify

import ZODB.blob
import BTrees.OOBTree
import ZConfig
import persistent
import transaction

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.thread

import zope.app.appsetup.product
import zope.app.component.interfaces
import zope.app.component.hooks

from zeit.connector.dav import (davresource, davconnection)
from zeit.connector.dav.davconnection import DAVConnection
from zeit.connector.dav.davresource import (
    DAVResource, DAVCollection, DAVFile, DAVError, DAVLockedError, DAVLockFailedError)

import zeit.connector.cache
import zeit.connector.interfaces
import zeit.connector.lockinfo
import zeit.connector.resource
import zeit.connector.search


logger = logging.getLogger(__name__)

# The property holding the "resource type".
RESOURCE_TYPE_PROPERTY = ('type', 'http://namespaces.zeit.de/CMS/meta')

# Highest possible datetime value. We use datetime-with-timezone everywhere.
# The MAXYEAR-1 is there to protect us from passing this bound when
# transforming into some local time
TIME_ETERNITY = datetime.datetime(
    datetime.MAXYEAR - 1, 12, 31, 23, 59, 59, 999999, tzinfo=pytz.UTC)

# Gaah. They stole print()
# That's what I _hate_ about Python culture. They assume to know
# what's good for you.
def holler(txt):
    sys.__stdout__.write(txt)

class DAVUnexpectedResultError(DAVError):
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

def _id_splitlast(id):
    # Split id in parent/name parts
    # FIXME fix borderline cases: _splitlast(""), _splitlast("/")
    parent, last = id.rstrip('/').rsplit('/', 1)
    return parent + '/', last

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


class Connector(zope.thread.local):
    """Connect to the CMS backend.
       WebDAV implementation based on pydavclient
    """

    zope.interface.implements(zeit.connector.interfaces.IConnector)

    def __init__(self, roots={}, prefix=u'http://xml.zeit.de/'):
        # NOTE: roots['default'] should be defined
        self._roots = roots # "extra" roots, a dict. ATM only xroots['search']
        self._conns = {} # conn cache for above. Hrrgrr. WARNING: indexed by netloc!
        self._prefix = prefix

    def _conn(self, root='default'):
        """Try to get a cached connection suitable for url"""
        # FIXME: someone will have to invalidate the connections at some point.
        url = self._roots[root]
        (scheme, netloc) = urlparse.urlsplit(url)[0:2]
        snetloc = "%s://%s" % (scheme, netloc)
        try: # grmblmmblpython
            host, port = netloc.split(':', 1)
            port = int(port)
        except ValueError:
            host, port = netloc, None
        # FIXME: Argh. DAVConnection should take schema as well!!!
        return DAVConnection(host, port)

    def listCollection(self, id):
        """List the filenames of a collection identified by <id> (see[8]). """
        # FIXME
        # Performance notes [4]:
        # This one slurps a list of names, keeps a copy and deals name
        # by name via yield(). Our provider, DavCollection, also has a
        # list of (whatever). It might make sense pushing the iterator
        # one layer deeper. But there are other worries (do we get one
        # DAV access per child if our clients request details about our
        # children? Probably yes!
        __traceback_info__ = (id, )
        id = self._get_cannonical_id(id)
        for child_id in self._get_resource_child_ids(id):
            if child_id != child_id.encode('ascii', 'replace'):
                # We want to ignore objects with strange characters in the id.
                continue
            yield (_id_splitlast(child_id)[1], child_id)

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
        cache = self.property_cache
        try:
            properties = cache[id]
        except KeyError:
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
            cache[response_id] = response.get_all_properties()
            cache[response_id][('cached-time', 'INTERNAL')] = now

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
        cache = self.body_cache
        try:
            data = cache.getData(id, properties)
        except KeyError:
            logger.debug("Getting body from dav: %s" % id)
            data = self._get_dav_resource(id).get()
            data = cache.setData(id, properties, data)
        if data is None:
            # This apparently happens when the resource does not have a
            # body but only properties.
            data = StringIO.StringIO()
        return data

    def __getitem__(self, id):
        __traceback_info__ = (id, )
        id = self._get_cannonical_id(id)
        try:
            content_type = self._get_resource_properties(id).get(
                ('getcontenttype', 'DAV:'))
        except davresource.DAVNotFoundError:
            raise KeyError("The resource %r does not exist." % id)
        return zeit.connector.resource.CachedResource(
            id, _id_splitlast(id)[1],
            self._get_resource_type(id),
            lambda: self._get_resource_properties(id),
            lambda: self._get_resource_body(id),
            content_type=content_type)

    def __setitem__(self, id, object):
        id = self._get_cannonical_id(id)
        resource = zeit.connector.interfaces.IResource(object)
        resource.id = id # override
        self._internal_add(id, resource)

    def __delitem__(self, id):
        # FIXME lotsa error checking here...
        id = self._get_cannonical_id(id)
        parent, name = _id_splitlast(id)
        try:
            self._get_dav_resource(parent).delete(
                name, self._get_my_locktoken(id))
        except davresource.DAVLockedError:
            raise zeit.connector.interfaces.LockingError(
                id, "Could not delete resource.")
        self._invalidate_cache(id)

    def __contains__(self, id):
        # Because we cache a lot it will be ok to just grab the object:
        try:
            self[id]
        except KeyError:
            return False
        return True

    def add(self, object):
        resource = zeit.connector.interfaces.IResource(object)
        id = self._get_cannonical_id(resource.id)
        self._internal_add(id, resource)

    def move(self, old_id, new_id):
        """Move the resource with id `old_id` to `new_id`."""

        if self._get_cannonical_id(new_id) in self:
            raise zeit.connector.interfaces.MoveError(
                old_id,
                "Could not move %s to %s, because target alread exists." % (
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
        conn = self._conn('default')
        conn.move(old_loc, new_loc)
        self._invalidate_cache(old_id)
        self._invalidate_cache(new_id)

    def changeProperties(self, id, properties):
        id = self._get_cannonical_id(id)
        locktoken = self._get_my_locktoken(id)
        davres = self._get_dav_resource(id)
        davres.change_properties(
            properties,
            delmark=zeit.connector.interfaces.DeleteProperty,
            locktoken=locktoken)
        self._invalidate_cache(id)


    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        url = self._id2loc(self._get_cannonical_id(id))
        token = None
        try:
            # NOTE: _timeout() returns None for timeouts too long. This blends
            #       with DAVConnection, which converts None to 'Infinite'.
            token = self._conn().do_lock(url,
                                         owner=principal,
                                         depth=0,
                                         timeout=_abs2timeout(until))
        except davresource.DAVLockedError:
            raise zeit.connector.interfaces.LockingError(
                id, "%s is already locked." % id)
        # Just pass-on other exceptions. It's more informative

        # FIXME [11] returning locktoken (DAV resources keep one...)
        if token: self._put_my_lockinfo(id, token, principal, until)
        self._invalidate_cache(id)
        return token

    def unlock(self, id, locktoken=None):
        url = self._id2loc(self._get_cannonical_id(id))
        locktoken = locktoken or self._get_dav_lock(id).get('locktoken')
        if locktoken:
            try:
                self._conn().do_unlock(url, locktoken)
            finally:
                self._put_my_lockinfo(id, None)
        self._invalidate_cache(id)

    def locked(self, id):
        id = self._get_cannonical_id(id)
        davlock = self._get_dav_lock(id)
        mylock = self._get_my_lockinfo(id)

        if mylock and mylock[0] != davlock.get('locktoken'): # Uh, oh
            #raise("Aaaah! Pirates!")
            self._put_my_lockinfo(id, None)
            mylock = None
            # Our lock was stolen. Are we supposed to scream? 
            # No we are not.

        owner = davlock.get('owner', None)
        timeout = davlock.get('timeout', None)

        if timeout == 'Infinite':
            timeout = TIME_ETERNITY

        return (owner, timeout, mylock is not None)

    def search(self, attrlist, expr):
        """Search repository behind this connector according to <expr>.
           For each match return the values of the attributes
           specified in attrlist
        """
        # Collect "result" vars as bindings "into" expression:
        for at in attrlist:
            expr = at.bind(zeit.connector.search.SearchSymbol('_')) & expr

        # Do we need a different conn for SEARCH?
        # NOTE: this code may become obsolete.
        #       We need it now to use a different netloc for different xconns.
        conn = self._conn('search')

        davres = davresource.DAVResult(
               conn.search(self._roots.get('search', self._roots['default']),
                            body=expr._collect()._render()))
        for url, resp in davres.responses.items():
            try:
                id = self._loc2id(urlparse.urljoin(self._roots['default'], url))
            except ValueError:
                # Search returns documents which are outside the root, ignore
                continue
            props = resp.get_all_properties()
            yield tuple([id] + [props[(a.name, a.namespace)] for a in attrlist])

    def _get_my_lockinfo(self, id): # => (token, principal, time)
        return self.locktokens.get(id)

    def _put_my_lockinfo(self, id, token, principal=None, time=None):
        # FIXME better defaults
        if token is None:
            self.locktokens.remove(id)
        else:
            self.locktokens.set(id, (token, principal, time))

    def _get_my_locktoken(self, id):
        try:
            locker, until, myself = self.locked(id)
        except KeyError:
            locktoken = None
        else:
            if locker and not myself:
                raise zeit.connector.interfaces.LockedByOtherSystemError(
                    id, locker, until)
        lock_info = self._get_my_lockinfo(id)
        if lock_info:
            token = lock_info[0]
        else:
            token = None
        return token

    def _id2loc(self, id):
        """Transform an id to a location, e.g.
             http://xml.zeit.de/2006/12/ -->
             http://zip4.zeit.de:9999/cms/work/2006/12/
           Just a textual transformation: replace _prefix with _root"""
        if id.startswith(self._prefix):
            return self._roots['default'] + id[len(self._prefix):]
        else:
            raise ValueError("Bad id %r (prefix is %r)" % (id, self._prefix))

    def _loc2id(self, loc):
        """Transform a location to an id, e.g.
             http://zip4.zeit.de:9999/cms/work/2006/12/ -->
             http://xml.zeit.de/2006/12/
           Just a textual transformation: replace _root with _prefix"""
        root = self._roots['default']
        if loc.startswith(root):
            return self._prefix + loc[len(root):]
        else:
            raise ValueError("Bad location %r (root is %r)" % (loc, root))

    def _internal_add(self, id, resource):
        """The grunt work of __setitem__() and add()
        """
        locktoken = self._get_my_locktoken(id) #  FIXME [7] [16]
        autolock = (locktoken is None)
        iscoll = (resource.type == 'collection'
                  or resource.contentType == 'httpd/unix-directory')
        if iscoll and not id.endswith('/'):
            id = id + '/'

        # No meaningful lock-null resources for collections :-(
        if autolock and not iscoll:
            locktoken = self.lock(id, "AUTOLOCK",
                                  datetime.datetime.now(pytz.UTC) +
                                  datetime.timedelta(seconds=20))

        if hasattr(resource.data, 'seek'):
            resource.data.seek(0)
        data = resource.data.read() # FIXME [17]: check possibility to pass data as IO object

        if iscoll:
            if not self._check_dav_resource(id):
                self._add_collection(id)
            davres = self._get_dav_resource(id, ensure='collection')
            # NOTE: here be race condition. Lock-null trick doesn't work,
            #       so we lock _after_ creation
            if autolock:
                locktoken = self.lock(id, "AUTOLOCK",
                                      datetime.datetime.now(pytz.UTC) +
                                      datetime.timedelta(seconds=20))
        else: # We are a file resource:
            if(self._check_dav_resource(id) is None):
                (parent, name) = _id_splitlast(id)
                parent = self._get_dav_resource(parent, ensure='collection')
                davres = parent.create_file(name, data, resource.contentType,
                                            locktoken = locktoken)
            else:
                davres = self._get_dav_resource(id, ensure='file')
                davres.upload(data, resource.contentType,
                              locktoken = locktoken)

        # Set the resource type from resource.type.
        properties = dict(resource.properties)
        properties[RESOURCE_TYPE_PROPERTY] = resource.type
        __traceback_info__ = (
            dict(properties), zeit.connector.interfaces.DeleteProperty)
        davres.change_properties(
            properties,
            delmark=zeit.connector.interfaces.DeleteProperty,
            locktoken=locktoken)

        if autolock and locktoken: # This was _our_ lock. Cleanup:
            self.unlock(id, locktoken=locktoken)
        self._invalidate_cache(resource.id)

    def _add_collection(self, id):
        # NOTE id is the collection's id. Trailing slash is appended as necessary.
        # We assume id to map to a non-existent resource, its
        # parent is assumed to exist.
        if not id.endswith('/'):
            id += '/'
        conn = self._conn()
        url = self._id2loc(id)
        davres = davresource.DAVResult(conn.mkcol(url))
        if davres.has_errors():
            raise DAVError, (davres,)

    def _check_dav_resource(self, id):
        """Check whether resource <id> exists.
           Issue a head request and return not None when found.
           (Actually return the ETag, but don't rely on that yet)
        """
        url = self._id2loc(id)
        hresp = DAVResource(url, conn=self._conn()).head()
        if not hresp:
            return None # FIXME throw exception?
        st = int(hresp.status)
        if  st== httplib.OK:
            return hresp.getheader('ETag', 'Unspecified ETag')
        elif st == httplib.NOT_FOUND:
            return None
        else:
            raise DAVUnexpectedResultError, \
                  ('Unexpected result code for %s: %d' % (url, st))

    def _get_dav_resource(self, id, ensure=None):
        """returns resource corresponding to <id>, which see [8],
        <ensure> may be 'file' or 'collection'"""
        # FIXME [14] Make DAVResource() return appropriate sub-type
        url = self._id2loc(id)
        # FIXME here, we tacitly assume that URIs ending with '/' MUST
        # be collections. This ain't strictly right
        wantcoll = (ensure == 'collection' or url.endswith('/'))
        try:
            if wantcoll:
                res = DAVCollection(url, conn = self._conn()) # FIXME auto_request?
            elif ensure == 'file':
                res = DAVFile(url, conn = self._conn()) # FIXME auto_request?
            else: # Tis one to disappear when [14] fixed
                res = DAVResource(url, conn = self._conn()) # FIXME auto_request?
        except:
            raise # FIXME: anything goes here :-/
        return res

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
                    reftime = self[id].properties[('cached-time', 'INTERNAL')]
                    timeout = reftime + datetime.timedelta(
                        seconds=int(m.group(1)))
                davlock['timeout'] = timeout

            davlock['locktoken'] = unicode(lockinfo_node.locktoken.href)
        return davlock

    def _invalidate_cache(self, id):
        # TODO: In the ZopeConnector we might use an event for invalidation.
        parent, last = _id_splitlast(id)
        for cache, key in ((self.property_cache, id),
                           (self.child_name_cache, id),
                           (self.property_cache, parent),
                           (self.child_name_cache, parent)):
            try:
                del cache[key]
            except KeyError:
                pass

    def _get_cannonical_id(self, id):
        """Add / for collections if not appended yet."""
        if id == self._prefix:
            return id
        if id.endswith('/'):
            id = id[:-1]
        if self.property_cache.get(id + '/') is not None:
            return id + '/'
        if self.property_cache.get(id) is not None:
            return id
        dav_resource = DAVResource(self._id2loc(id + '/'), conn=self._conn())
        if dav_resource.head().status == 200:
            return id + '/'
        return id

    @zope.cachedescriptors.property.Lazy
    def body_cache(self):
        return zeit.connector.cache.ResourceCache()

    @zope.cachedescriptors.property.Lazy
    def property_cache(self):
        return {}

    @zope.cachedescriptors.property.Lazy
    def child_name_cache(self):
        return {}

    @zope.cachedescriptors.property.Lazy
    def locktokens(self):
        return zeit.connector.lockinfo.LockInfo()


class ZopeConnector(Connector):

    @property
    def body_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IResourceCache)

    @property
    def property_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IPropertyCache)

    @property
    def child_name_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IChildNameCache)

    @property
    def locktokens(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.ILockInfoStorage)


def connectorFactory():
    """Factory for creating the connector with data from zope.conf."""
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    if config:
        root = config.get('document-store')
        if not root:
            raise ZConfig.ConfigurationError(
                "WebDAV server not configured properly.")
        search_root = config.get('document-store-search')
    else:
        root = os.environ.get('connector-url')
        search_root = os.environ.get('search-connector-url')

    if not root:
        raise ZConfig.ConfigurationError(
            "zope.conf has no product config for zeit.connector.")

    return ZopeConnector(dict(
        default=root,
        search=search_root))
