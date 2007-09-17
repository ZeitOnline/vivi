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
# [10] we'll have to enhance it anyway because it doesn't support setting
#      lock expiry.
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

import StringIO
import datetime
import httplib
import random
import time
import urlparse

import gocept.lxml.objectify

import ZODB.blob
import BTrees.OOBTree
import ZConfig
import persistent
import transaction

import zope.component
import zope.interface
import zope.thread

import zope.app.appsetup.product
import zope.app.component.interfaces
import zope.app.component.hooks

from zeit.connector.dav import davresource
from zeit.connector.dav.davresource import (
    DAVResource, DAVCollection, DAVFile, DAVError)

import zeit.connector.interfaces
import zeit.connector.search
import zeit.connector.resource


# The property holding the "resource type".
# Note that davlib takes (name, namespace). Ugh.
PROP_RESTYPE = ('type', 'http://namespaces.zeit.de/CMS/document')

# Gaah. They stole print()
# That's what I _hate_ about Python culture. They assume to know
# what's good for you.
import sys
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


def connectorFactory():
    cms_config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    if not cms_config:
        raise ZConfig.ConfigurationError(
            "zope.conf has no product config for zeit.cms.")
    root = cms_config.get('document-store')
    if not root:
        raise ZConfig.ConfigurationError(
            "WebDAV server not configured properly.")
    return Connector(root)


class Connector(zope.thread.local):
    """Connect to the CMS backend.
       WebDAV implementation based on pydavclient
    """

    zope.interface.implements(zeit.connector.interfaces.IConnector)

    def __init__(self, root, prefix=u'http://xml.zeit.de/'):
        self._root = root # FIXME check that to be a legal URL. Perhaps canonicalize
        self._prefix = prefix
        ( self._root_schema,
          self._root_netloc,
          self._root_path,
          self._root_query,
          self._root_frag )   = urlparse.urlsplit(root)
        self._conn = None

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
        if not id.endswith('/'):
            id = id + '/'
        for child_id in self._get_resource_child_ids(id):
            if child_id != child_id.encode('ascii', 'replace'):
                # We want to ignore objects with strange characters in the id.
                continue
            yield (_id_splitlast(child_id)[1], child_id)

    def _get_resource_type(self, id):
        __traceback_info__ = (id, )
        properties = self._get_resource_properties(id)
        r_type = properties.get(PROP_RESTYPE)
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
        cache = self.cache
        try:
            properties = cache.properties[id]
        except KeyError:
            davres = self._get_dav_resource(id)
            if davres._result is None:
                davres.update()
            self._update_property_cache(davres)
            self._update_child_id_cache(davres)
            properties = davres.get_all_properties()
        return properties

    def _get_resource_child_ids(self, id):
        try:
            child_ids = self.cache.child_ids[id]
        except KeyError:
            davres = self._get_dav_resource(id)
            if davres._result is None:
                davres.update()
            self._update_property_cache(davres)
            child_ids = self._update_child_id_cache(davres)
        return child_ids

    def _update_property_cache(self, dav_result):
        cache = self.cache.properties
        for path, response in dav_result._result.responses.items():
            response_id = self._loc2id(urlparse.urljoin(self._root, path))
            properties = cache[response_id] = response.get_all_properties()

    def _update_child_id_cache(self, dav_response):
        if not dav_response.is_collection():
            return
        id = self._loc2id(urlparse.urljoin(self._root, dav_response.path))
        child_ids = self.cache.child_ids[id] = [
            self._loc2id(urlparse.urljoin(self._root, path))
            for path in dav_response.get_child_names()]
        return child_ids

    def _get_resource_body(self, id):
        """Return body of resource."""
        __traceback_info__ = (id, )
        properties = self._get_resource_properties(id)
        cache = self.cache
        try:
            data = cache.getData(id, properties)
        except KeyError:
            data = self._get_dav_resource(id).get()
            data = cache.setData(id, properties, data)
        return data

    def __getitem__(self, id):
        __traceback_info__ = (id, )
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

    def __setitem__(self, id, object): # FIXME id or path? see [3], [3a]
        resource = zeit.connector.interfaces.IResource(object)
        resource.id = id # override
        self._internal_add(id, resource)

    def __delitem__(self, id):
        # FIXME lotsa error checking here...
        parent, name = _id_splitlast(id)
        self._get_dav_resource(parent).delete(name, self._get_my_locktoken(id))

    def add(self, object):
        resource = zeit.connector.interfaces.IResource(object)
        self._internal_add(resource.id, resource)

    def changeProperties(self, id, properties):
        locktoken = self._get_my_locktoken(id)
        davres = self._get_dav_resource(id)
        davres.change_properties(
            properties,
            delmark=zeit.connector.interfaces.DeleteProperty,
            locktoken=locktoken)
        self._invalidate_cache(id)

    def lock(self, id, principal, until):
        """Lock resource for principal until a given datetime."""
        # FIXME [9] lock non-existing resources as well?
        davres = self._get_dav_resource(id)
        try:
            # FIXME [10] expiry, i.e. until
            token = davres.lock(owner=principal, depth=0)
        except davresource.DAVLockedError:
            raise zeit.connector.interfaces.LockingError(
                "%s is already locked." % id)
        except: # FIXME how to get at exception info
            # FIXME [13]: refine LockingError, how?
            ### type, value, traceback = sys.exc_info()
            raise zeit.connector.interfaces.LockingError(
                "DAV error %s on %s" % ("UNKNOWN", id))
        # FIXME [11] returning locktoken (DAV resources keep one...)
        self._put_my_lockinfo(id, token, principal, until)
        self._invalidate_cache(id)
        return token

    def unlock(self, id):
        tok = self._get_my_locktoken(id)
        if tok:
            davres = self._get_dav_resource(id)
            try:
                try:
                    davres.unlock(locktoken=tok)
                finally:
                    self._put_my_lockinfo(id, None)
            except:
                # FIXME [13]: refine LockingError, how?
                raise
#                raise zeit.cms.interfaces.LockingError("DAV error %s on %s" \
#                                                    % ("UNKNOWN", id))
        self._invalidate_cache(id)

    def locked(self, id):
        lockdiscovery = self[id].properties[('lockdiscovery', 'DAV:')]
        if not lockdiscovery:
            return (None, None, False)

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
            davlock['timeout']   = unicode(lockinfo_node.timeout)
            davlock['locktoken'] = unicode(lockinfo_node.locktoken.href)

        mylock = self._get_my_lockinfo(id)

        if mylock and mylock[0] != davlock.get('locktoken'): # Uh, oh
            raise("Aaaah! Pirates!")
            self._put_my_lockinfo(id, None)
            mylock = None
            # Our lock was stolen. Are we supposed to scream?

        owner = davlock.get('owner', None)
        timeout = davlock.get('timeout', None)

        if owner == 'None':
            owner = None
        if timeout == 'Infinite':
            timeout = datetime.datetime.max

        return (owner, timeout, mylock is not None)

    def search(self, attrlist, expr):
        """Search repository behind this connector according to expression expr
           For each match return the values of the attributes specified in attrlist
        """
        for at in attrlist:
            expr = at.bind('_') & expr
        # do something with return expr._collect()._render()
        holler("---SEARCH---\n%s\n------------\n" % expr._collect()._render()) # twice _collect() should be idempotent
        r = self._get_dav_resource(self._prefix) # FIXME: Dirty trick to make sure we have a _conn
        return [resp.get_all_properties() \
                    for resp in davresource.DAVResult(self._conn.search(expr._collect()._render())).responses]

    def _get_my_lockinfo(self, id): # => (token, principal, time)
        return self.cache.locktokens.get(id)

    def _put_my_lockinfo(self, id, token, principal=None, time=None): # FIXME better defaults
        locktbl = self.cache.locktokens
        if token is None:
            if locktbl.has_key(id):
                del locktbl[id]
        else:
            locktbl[id] = (token, principal, time)

    def _get_my_locktoken(self, id):
        l = self._get_my_lockinfo(id)
        if l: tok = l[0]
        else: tok = None
        return tok

    def _id2loc(self, id):
        """Transform an id to a location, e.g.
             http://xml.zeit.de/2006/12/ -->
             http://zip4.zeit.de:9999/cms/work/2006/12/
           Just a textual transformation: replace _prefix with _root"""
        if id.startswith(self._prefix):
            return self._root + id[len(self._prefix):]
        else:
            raise ValueError("Bad id %r (prefix is %r)" % (id, self._prefix))

    def _loc2id(self, loc):
        """Transform a location to an id, e.g.
             http://zip4.zeit.de:9999/cms/work/2006/12/ -->
             http://xml.zeit.de/2006/12/
           Just a textual transformation: replace _root with _prefix"""
        if loc.startswith(self._root):
            return self._prefix + loc[len(self._root):]
        else:
            raise ValueError("Bad location %r (root is %r)" % (loc, self._root))

    def _internal_add(self, id, resource):
        """The grunt work of __setitem__() and add()
        """
        try:
            locker, until, myself = self.locked(id)
        except KeyError:
            locktoken = None
        else:
            if not myself:
                raise Exception("Locked by other system.")
            locktoken = self._get_my_locktoken(id) #  FIXME [7] [16]

        autolock = (locktoken is None)
        if autolock:
            locktoken = self.lock(id, "AUTOLOCK",
                                  datetime.datetime.today() + \
                                      datetime.timedelta(seconds=20))
        if hasattr(resource.data, 'seek'):
            resource.data.seek(0)
        data = resource.data.read()
        if(self._check_dav_resource(id) is None):
            (parent, name) = _id_splitlast(id)
            parent = self._get_dav_resource(parent, ensure='collection')
            davres = parent.create_file(name, data, resource.contentType,
                                        locktoken = locktoken)
        else:
            davres = self._get_dav_resource(id, ensure='file')
            davres.upload(data, resource.contentType,
                          locktoken = locktoken)

        davres.change_properties(
            resource.properties,
            delmark=zeit.connector.interfaces.DeleteProperty,
            locktoken=locktoken)
        if autolock:
            self.unlock(id)
        self._invalidate_cache(resource.id)

    def _check_dav_resource(self, id):
        """Check whether resource <id> exists.
           Issue a head request and return not None when found.
           (Actually return the ETag, but don't rely on that yet)
        """
        url = self._id2loc(id)
        hresp = DAVResource(url, conn=self._conn).head()
        if hresp:
            if self._conn is None:
                self._conn = hresp._conn # cache DAV connection
        else:
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
                res = DAVCollection(url, conn = self._conn) # FIXME auto_request?
            elif ensure == 'file':
                res = DAVFile(url, conn = self._conn) # FIXME auto_request?
            else: # Tis one to disappear when [14] fixed
                res = DAVResource(url, conn = self._conn) # FIXME auto_request?
        except:
            raise # FIXME: anything goes here :-/
        if res._conn is None:
            res.connect()
        if res and self._conn is None:
            self._conn = res._conn # cache DAV connection
        return res

    def _invalidate_cache(self, id):
        parent, last = _id_splitlast(id)
        for cache, key in ((self.cache.properties, id),
                           (self.cache.child_ids, id),
                           (self.cache.properties, parent),
                           (self.cache.child_ids, parent)):
            try:
                del cache[key]
            except KeyError:
                pass

    @property
    def cache(self):
        site = zope.app.component.hooks.getSite()
        return zeit.connector.interfaces.IResourceCache(site)
