"""Module containing classes for client-side WebDAV access.

DAVResource is the class to use; it points to a location (URL) and offers
some methods to retrieve informations about the refered to resource.
"""
import urllib
from urlparse import urlparse, urlunparse, urljoin
import httplib
import pprint
import re

import lxml.etree

import davbase, davconnection
from davxml import xml_from_string

# from debug import OUT
# OUT.color_off()

### What on earth is this supposed to do?
try:
    False
    True
except NameError:
    True = 1
    False = not True
    pass


_DEFAULT_OWNER = u'<DAV:href>pydav-client</DAV:href>'
_DEFAULT_OWNER2 = u'<DAV:href>pydav-client-2</DAV:href>'



#:note: Used to generate an 'If' header
def _mk_if_data ( url, locktoken ):
    s = '<%(url)s>(<%(locktoken)s>)' % locals()
    return s

_qname_pattern = re.compile("{(?P<uri>.+)}(?P<name>.+)")
def _make_qname_tuple(string, pattern=_qname_pattern):
    __traceback_info__ = (string,)
    match = pattern.match(string)
    return (match.group('name'), match.group('uri'))


#:fixme: refactor/rename: this is really _find_dav_children
#:note:  should we only look for direct children?
def _find_child ( node, name ):
    """Find all direct children of node with namespace 'DAV:' and name <name>"""
    res = node.xpath("D:%s" % (name,), namespaces={'D' : 'DAV:'})
    return res

class DAVError ( Exception ):
    """Generic DAV exception
    """
    pass


class DAVNoFileError ( DAVError ):
    """Exception raised if a DAVFile specific method is invoked on a collection.
    """
    pass


class DAVNoCollectionError ( DAVError ):
    """Exception raised if a collection specific method is invoked on a non-collection.
    """
    pass


class DAVNotFoundError ( DAVError ):
    """Exception raised if a resource or a property was not found.
    """
    pass


class DAVNotConnectedError ( DAVError ):
    """Exception raised if there is no connection to the server.
    """
    pass


class DAVLockFailedError ( DAVError ):
    """Exception raised if an attempt to lock a resource failed.
    """
    pass


class DAVUnlockFailedError ( DAVError ):
    """Exception raised if an attempt to lock a resource failed.
    """
    pass


#:fixme: Maybe we should report information about the lock status as well ...
class DAVLockedError ( DAVError ):
    """Exception raised if an atempt to modify or lock a locked resource was
    made.
    """


#:fixme: Maybe we should report information about the lock status as well ...
class DAVNotLockedError ( DAVError ):
    """Exception raised if an atempt to unlock a not locked resource was made.
    """
    pass


#:fixme: Maybe we should report information about the lock status as well ...
class DAVNotOwnerError ( DAVError ):
    """Exception raised if an atempt to unlock a resource not owned was made.
    """
    pass


class DAVInvalidLocktokenError ( DAVError ):
    """Exception raised if an attempt to unlock a not locked resource was made.
    """
    pass


class DAVCreationFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """
    pass


class DAVUploadFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """
    pass


class DAVDeleteFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """
    pass

class DAVBadStatusLineError ( DAVError ):
    """Exception raised when we don't grok a status line
       (that's one of those "HTTP/1.1 200 OK" thingies around there)
    """
    pass

# As of rfc2616: 6.1 Status Line
_stat_patt = re.compile("^(HTTP/\d+\.\d+)\s+(\d\d\d)(?:\s+(.*))?$")

def _parse_status_line(line):
    line = line.strip("\r\n\t ")
    m = _stat_patt.match(line)
    # EEK! m==None should be caught by exception below, but isn't :-(
    if m is not None:
        # FIXME: we might try to grok protocol version (in m.group(1))
        stat, reason = m.group(2, 3)
        try:
            stat = int(stat)
        except ValueError:
            pass
        else:
            return stat, reason

    raise DAVBadStatusLineError("Can't grok status line %r" % line)

#:fixme: I don't like this setup: why group properties by their status code
# at all. Does a read operation on a property need to check in all DAVPropstat
# objects of a DAVResource?

class DAVPropstat:
    """
    """
    def __init__ ( self, doc, ps_node ):
        self.status = None
        self.reason = ''
        self.properties = {}
        self.locking_info = {}
        self.description = ''
        self._parse_ps(doc, ps_node)
        return

    #:new:
    #:fixme: do we need the document node here?  It would be
    # convenient iff we :ove xpath evaluation to the document object
    # (by calling doc.xpathEval(expr, context_node)
    def _parse_ps( self, doc, context_node ):
        status_nodes = context_node.xpath(
            'D:status', namespaces={'D' : 'DAV:'})
        # Huzzah for copy&paste programming :-(
        if status_nodes: # FIXME: What when more than one?
            # may raise exception
            self.status, self.reason = _parse_status_line(status_nodes[0].text)

        # description
        desc = context_node.xpath(
            'D:responsedescription', namespaces={'D' : 'DAV:'})
        if desc:
            self.description = desc[0].text.strip()
        # parse property name/value pairs
        prop_nodes = context_node.xpath(
            'D:prop/*', namespaces={'D' : 'DAV:'})
        for prop in prop_nodes:
            pkey   = _make_qname_tuple(prop.tag)
            #:fixme: is strip() correct here?
            # And what about structured values?
            if  len(prop) < 1:
                 pvalue = prop.text # .strip()
            else:
                 pvalue = lxml.etree.tostring(prop)
                 # pvalue = etree.tostring(Etree(prop))
            # pprint({'name':pkey, 'value':pvalue})
            self.properties[pkey] = pvalue
        # "special" properties
        # DAV:
        #:fixme: can we use restype = doc.xpathEval(path, ps_node)
        # Why this extra scan? {DAV:}resourcetype should be set during
        # the above iteration
        restype = context_node.xpath(
            'D:prop/D:resourcetype/*', namespaces={'D' : 'DAV:'})
        if not restype:
            # resourcetype not filled
            # This is plain and simple wrong!
            pass
        # locking info
        linfo = {}
        lockinfo_nodes = context_node.xpath(
            'D:prop/D:lockdiscovery/D:activelock',
            namespaces={'D' : 'DAV:'})
        if len(lockinfo_nodes) > 1:
            raise "Malformed PROPSTAT respones: more than one activlock found!"
        if lockinfo_nodes:
            context = lockinfo_nodes[0]
           #:fixme: the following would be prominent calls for 
           # find_first_child(...)
            try:
                linfo['owner'] = context.xpath(
                    'D:owner', namespaces={'D' : 'DAV:'})[0].text.strip()
            except IndexError:
                linfo['owner'] = None
                pass
            linfo['timeout']   = context.xpath(
                'D:timeout', namespaces={'D' : 'DAV:'})[0].text.strip()
            linfo['locktoken'] = context.xpath(
                'D:locktoken/D:href', namespaces={'D' : 'DAV:'})[0].text.strip()
        self.locking_info = linfo
        return

    def has_errors ( self ):
        s = self.status
        if s is not None and s >= 300:
            return True
        return False

    def __repr__ ( self ):
        return "DAVPropstat: Status: %r %r %r\n" % (self.status, self.reason, self.description) + \
               "  Properties:" + pprint.pformat(self.properties, 2) + \
               "\n  Locking info: " + pprint.pformat(self.locking_info, 2)


class DAVResponse:
    """FIXME: document
    """
    def __init__ ( self, doc, res_node ):
        self.propstats = []
        self.url    = None
        self.status = None
        self.reason = None
        self._parse_res(doc, res_node)
        return

    #:new:
    def _parse_res ( self, doc, res_node ):
        href_nodes = _find_child(res_node, 'href')
        if not href_nodes:
            raise DAVNotFoundError, ('No href found in node %s!' % res_node.nodePath())  #:fixme: nodePath() is libxml2
        url_node = href_nodes[0]
        # self.url = urllib.unquote(url_node.text.strip()).decode('utf8')
        self.url = url_node.text.strip()
        status_nodes = _find_child(res_node, 'status')
        if status_nodes: # FIXME: What when more than one?
            # may raise exception
            self.status, self.reason = _parse_status_line(status_nodes[0].text)

        pslist = _find_child(res_node, 'propstat')
        for node in pslist:
            ps = DAVPropstat(doc, node)
            self.propstats.append(ps)
        return

    def has_errors ( self ):
        s = self.status
        if s is not None and s >= 300:
            return True
        for p in self.propstats:
            if p.has_errors():
                return True
        return False

    def propstat_count ( self ):
        return len(self.propstats)

    def get_propstat ( self, idx=0 ):
        return self.propstats[idx]

    def get_all_properties ( self ):
        ret = {}
        psl = [ ps.properties for ps in self.propstats if ps.status < 300 ]
        for p in psl:
            ret.update(p)
        return ret

    def get_locking_info ( self ):
        ret = {}
        iil = [ ps.locking_info for ps in self.propstats if ps.status < 300 ]
        for i in iil:
            ret.update(i)
        return ret

    def __repr__ ( self ):
        return "  DAVResponse for %s: %r %r\n  " % (self.url, self.status, self.reason) + \
        "\n  ".join([p.__repr__() for p in self.propstats])


class DAVResult:

    def __init__ ( self, http_response=None ):
        """Initialize a DAVResult instance.

        If http_response is given (and a httplib.HTTPResponse instance)
        the status code and the reason are copied.

        If the status code equals 207 (Multi-Status), the body of
        the response is read and parsed.
        """
        self.responses = {}
        self.etag = self.status = self.reason = None
        if http_response is None:
            return
        data = http_response.read()
        self.status = int(http_response.status)
        self.reason = http_response.reason
        self.etag   = http_response.getheader('ETag', None)
        self.lock_token = http_response.getheader('Lock-Token', None)
        if self.lock_token and self.lock_token[0] == '<':
            self.lock_token = self.lock_token[1:-1]
        if self.status != 207:
            return
        self.parse_data(data)
        return

    def parse_data ( self, data ):
        doc = xml_from_string(data)
        self._parse_response(doc)

    def _parse_response ( self, doc ):
        self.responses = {}
        responses = doc.get_response_nodes()
        r_urls = []
        for node in responses:
            r = DAVResponse(doc, node)
            self.responses[r.url] = r
            r_urls.append(r.url)
        return

    def has_errors ( self ):
        if self.status >= 300:
            return True
        for r in self.responses.values():
            if r.has_errors():
                return True
        return False

    def response_count ( self ):
        return len(self.responses)

    def get_response ( self, uri ):
	# Try both variants:
        try:
            return self.responses[uri]
        except KeyError:
            if uri.endswith('/'): uri = uri[0:-1]
            else: uri += '/'
            return self.responses[uri]

    def get_locktoken ( self, url ):
        r  = self.get_response(url)
        li = r.get_locking_info()
        if li.has_key('locktoken'):
            return li['locktoken']
        return None

    def get_etag ( self, url ):
        r = self.get_response(url)
        pd = r.get_all_properties()
        etag = pd.get(('getetag','DAV:'), None)
        return etag

    def __repr__ ( self ):
        return "=== DAVResult ===" + \
               ("  Status: %d %s\n  " % (self.status, self.reason)) + \
               "\n  ".join([r.__repr__() for r in self.responses.values()]) + \
               "\n=================\n"

class DAVResource:
    """Basic class describing an arbitrary DAV resource (file or collection)
    """

    def __init__ ( self, url, conn=None, auto_request=False ):
        """Setup a fresh instance.
        """
        self._set_url(url)
        self.auto_request = auto_request
        self.collection = None
        self.size       = None
        self.locktoken  = None
        self._conn      = conn
        self._result    = None
        return

    def _set_url ( self, url ):
        # extract server/port from url, needed for DAV
        self.url    = url
        url_tuple   = urlparse(url, 'http', 0)
        self.scheme = url_tuple[0]
        self.host   = url_tuple[1]
        self.path   = url_tuple[2]
        return

    def _make_url_for ( self, path ):
        t = (self.scheme, self.host, path) + ('','','')
        return urlunparse(t)

    #:fixme: this is rather strange -- not the way to do it
    def get_server ( self ):
        return self._make_url_for('/')

    def invalidate ( self ):
        """Invalidate the internal cache, so that the next method call will
        invoke a request to the server.
        """
        self.size = None
        self.etag = None
        self.collection = None
        self._result = None
        return

    def update ( self, conn=None, depth=0 ):
        """Update all local data for this resource.

        Returns a DAVResult instance as result.
        This result is also stored internally, so don't mess with it.

        Issues a propfind request with depth 'depth' to the server.

        If the conn parameter is not None, it sets the connection to the
        given one.
        """
        if conn is not None:
            self.set_connection(conn)
        else:
            self.invalidate() # just to be sure
        try:
            self._result = self._propfind(depth=depth)
            #:fixme: this is brittle: how should we represent ns/name pairs?
            # With tuples like the original code or in Clark notation?
            v = self.get_property_value( ('resourcetype', 'DAV:') )
            self.collection = (v is not None) and (v.find('collection') >= 0)
        except DAVError, ex:
            if ex.args[0] == 404:
                raise DAVNotFoundError(ex.args)
            else:
                raise
        return self._result

    def is_connected ( self ):
        """Return True if there is a connection established.
        """
        return self._conn is not None

    def set_connection ( self, conn ):
        """Set the connection.

        conn has to be a DAV instance from the davlib module.
        """
        self._conn = conn
        self.invalidate()
        return

    def connect ( self ):
        """Create a connection for this resource.
        """
        netloc = self.host
        host   = netloc.split(':')
        try:
            port = int(host[1])
        except (ValueError, IndexError):
            port = None
            pass
        con = davconnection.DAVConnection(host[0], port)
        self.set_connection(con)
        return

    def get_property_namespaces ( self ):
        """Return a list of tuples with all used namespace uris and their prefixes used for properties.
        """
        if self.auto_request or not self._result:
            self.update()
        result = self._result
        response = result.get_response(self.path)
        names = response.get_all_properties().keys()
        d = {}
        for name, ns in names:
            d[ns] = None
        return d.keys()

    def get_property_names ( self, nsuri=None ):
        """Return the names of all properties within the given namespace uri

        If nsuri is empty (or None), return all property names from all
        namespaces.

        The result is a list of tuples (name, nsuri).
        """
        props = []
        if self.auto_request or not self._result:
            self.update()
        result = self._result
        response = result.get_response(self.path)
        # get all properties
        if not nsuri:
            res = response.get_all_properties().keys()
        else:
            res = [ t for t in response.get_all_properties().keys() if t[1] == nsuri ]
        return res

    def get_property_value ( self, propname ):
        """Return the value of the given property.

        propname is a tuple of (name, nsuri).
        """
        if self.auto_request or not self._result:
            # no _result here yet
            self.update()
        #:fixme: this is fragile! Iff update() doesn't fill the
        # _result slot than we are stuck in a loop!
        result   = self._result
        response = result.get_response(self.path)
        props    = response.get_all_properties()
        ret      = props.get(propname, None)
        return ret

    def get_all_properties ( self ):
        r   = self._result.get_response(self.path)
        return r.get_all_properties()

    def get_etag ( self ):
        """Return the etag for this resource or None.
        """
        etag = self._result.get_etag(self.path)
        return etag

    def change_properties( self, pdict, delmark=None, locktoken=None):
        """Set, update or delete the properties in pdict on this resource.

        Delete properties when the property value _is_ delmark.

        Returns a DAVResult instance as result.

        The property names (keys of pdict) *have* to be tuples of (name,
        nsuri).  The property values *will* be xml escaped before they're
        stored.

        """
        if not pdict:
            return None

        set_properties = []
        delete_properties = []

        make_element = lambda namespace, name: (
            lxml.etree.Element('{%s}%s' % (namespace, name)))

        for (name, namespace), value in pdict.items():
            if namespace == 'DAV:':
                # We are not supposed to touch these (maybe others?)
                continue

            if value is delmark:  # delete
                delete_properties.append(
                    make_element(namespace, name))
            else:            # set/change
                # the values should be unicode. If they are not the we at least
                # try to make one. This is ok for ascii stirngs and breaks on
                # every encoded string. Just like it should.
                value = unicode(value)
                node = make_element(namespace, name)
                node.text = value
                set_properties.append(node)

        # NOTE: set_properties and delete_properties can't be both empty
        # because pdict isn't.

        body = make_element('DAV:', 'propertyupdate')
        def _append_change(name, nodes):
            if not nodes:
                return
            change_node = lxml.etree.Element(name)
            prop_node = lxml.etree.Element('{DAV:}prop')
            change_node.append(prop_node)
            prop_node.extend(nodes)
            body.append(change_node)

        _append_change('{DAV:}set', set_properties)
        _append_change('{DAV:}remove', delete_properties)

        xml_body = lxml.etree.tostring(body.getroottree(),
                                       encoding='UTF-8',
                                       xml_declaration=True)
        res = self._proppatch(xml_body, locktoken=locktoken)
        return res

    def is_collection ( self ):
        """Returns true if self refers to a collection.
        """
        if self.auto_request or not self._result:
            self.update()
        return self.collection

    def get ( self, xhdrs=None ):
        """Issue a get request to the url of this instance and return
        a httplib.HTTPResponse instance.
        """
        if xhdrs is None:
            xhdrs = {}
        res = self._conn.get(self.url, xhdrs)
        return res

    def head ( self, xhdrs=None ):
        """Issue a head request to the url of this instance and return
        a httplib.HTTPResponse instance.
        """
        if xhdrs is None:
            xhdrs = {}
        res = self._conn.head(self.url, xhdrs)
        return res

    def options ( self, xhdrs=None ):
        """Issue an options request to the url of this instance and return
        a dict containing the result.

        The resulting keys are: server, allow, dav
        """
        if xhdrs is None:
            xhdrs = {}
        res = self._conn.options(self.url, xhdrs)
        d = {}
        for k, v in res.msg.items():
            if k.lower() in ('dav','server','allow','ms-author-via'):
                d[k] = v
        return d

    def is_locked ( self ):
        """Return True if this resource is locked.
        """
        if self.auto_request or not self._result:
            self.update()
        result = self._result
        lt = result.get_locktoken(self.path)
        return bool(lt)

    def get_locking_info ( self ):
        """Query the server for locking information.

        The information is returned in a dict, which might be empty if no
        lock is on the resource.

        This method *always* issues a propfind request to the server!
        """
        ret = {}
        self.invalidate()
        if not self.is_locked():
            # short cut
            return ret
        response = self._result.get_response(self.path)
        li = response.get_locking_info()
        return li.copy()

    def _lock_path ( self, path, owner=None, depth=0, header=None ):
        if header is None:
            header = {}
        r = self._conn.lock(path, owner=owner, depth=depth, extra_hdrs=header)
        davres = DAVResult(r)
        return davres

    def _unlock_path ( self, path, locktoken, header=None ):
        if header is None:
            header = {}
        r = self._conn.unlock(path, locktoken, extra_hdrs=header)
        davres = DAVResult(r)
        return davres

    def lock ( self, owner=None, depth='0' ):
        """Lock the resource this instance refers to and return the locktoken.

        owner is a plain string or a xml fragment which is stored with the lock
        information.

        depth specifies the locking depth. Valid values are: 0 (default),
        1 and 'infinite' which might not be supported by the server.

        If the resource is already locked, DAVLockedError is raised.

        If the lock fails, DAVLockFailedError is raised.
        """
        davres = self._lock_path(self.path, owner, depth)
        if not davres.has_errors():
            self.locktoken = davres.lock_token
            return self.locktoken
        if davres.status == 423:
            raise DAVLockedError, (davres,)
        else:
            raise DAVLockFailedError, (davres,)

    def unlock ( self, locktoken=None, owner=None ):
        """Unlock this resource, if it is locked and the right locktoken is passed.

        The method does not return anything.

        If locktoken is None the method tries to use self.locktoken.
        If there is no locktoken or the locktoken doesn't mactch the required
        token, DAVInvalidLocktokenError is raised.
        """
        if locktoken is None: # no locktoken given, try ours
            locktoken = self.locktoken
        if not locktoken: # no locktoken available
            raise DAVInvalidLocktokenError
        # check if our locktoken matches the required one
        davres = self._unlock_path(self.url, locktoken)
        if not davres.has_errors():
            self.update()
            if self.locktoken == locktoken:
                self.locktoken = None
            return
        # FIXME Other exceptions here?
        raise DAVUnlockFailedError(davres)

    def _propfind ( self, depth=0 ):
        """Query all properties for this resource and return a DAVResult instance.
        """
        if not self.is_connected():
            self.connect()
        hdrs = {}
        # if we have a locktoken, supply it
        if self.locktoken is not None:
            if  self.locktoken[0] != '<':
                lt =  '<' + self.locktoken + '>'
            hdrs['Lock-Token'] = self.locktoken
            hdrs['If'] = '<%s>(%s)' % (self.url, lt)
        xml = lxml.etree.Element('{DAV:}propfind')
        xml.append(lxml.etree.Element('{DAV:}allprop'))
        xmlstr = lxml.etree.tostring(xml, encoding='UTF-8',
                                     xml_declaration=True)
        try:
            response = self._conn.propfind(self.url, body=xmlstr,
                                           depth=depth, extra_hdrs=hdrs)
        except davbase.RedirectError, err:
            new_url = err.args[0]
            self._set_url(new_url)
            # re-issue request
            response = self._conn.propfind(self.url, body=xmlstr,
                                           depth=depth, extra_hdrs=hdrs)
            pass
        davres = DAVResult(response)
        if davres.status >= 300: # or davres.status in (404,200):
            raise DAVError(davres.status, davres.reason, davres)
        return davres

    def _proppatch ( self, body, locktoken ):
        """Issue a PROPPATCH request with the given xml body.

        Returns a DAVResult instance as result.
        """
        __traceback_info__ = (body, )
        if not self.is_connected():
            self.connect()
        hdrs = {}
        # if we get (or have) a locktoken, supply it
        mytoken = locktoken or self.locktoken
        if mytoken is not None:
            if  mytoken[0] != '<':
                lt =  '<' + mytoken + '>'
            hdrs['Lock-Token'] = mytoken
            hdrs['If'] = '<%s>(%s)' % (self.url, lt)
        response = self._conn.proppatch(self.url, body=body, extra_hdrs=hdrs)
        davres = DAVResult(response)
        if davres.status in (200,404) or davres.status >= 300:
            raise DAVError, (davres.status, davres.reason, davres)
        return davres
#

class DAVFile ( DAVResource ):

    def __init__ ( self, url, conn=None, auto_request=False ):
        DAVResource.__init__(self, url, conn, auto_request)
        self.update()
        if self.is_collection():
            raise DAVNoFileError
        return

    def file_size ( self ):
        """Return the size of this DAVFile in bytes.

        The size is taken out of the getcontentlength property.
        If the getcontentlength property is not found, -1 is returned.
        """
        if self.auto_request or not self._result:
            self.update()
        try:
            fs = self.get_property_value( ('getcontentlength', 'DAV:') )
            if not fs:
                fs = 0
        except DAVNotFoundError:
            fs = -1
            pass
        self.size = int(fs)
        return self.size

    def upload ( self, data, mime_type=None, encoding=None, locktoken=None ):
        """Upload data to this file via a PUT request.
        """
        if mime_type is None:
            mime_type = 'application/octet-stream'
        self.update()
        mytoken = locktoken or self.locktoken
        if self.is_locked():
            linfo = self.get_locking_info()
            if not (mytoken and mytoken == linfo['locktoken']): # FIXME check this!
                raise DAVLockedError
        hdrs = {}
        if mytoken:
            hdrs['Lock-Token'] = '<' + mytoken + '>' # FIXME cf. _proppatch. Which is right?
            hdrs['If'] = '<%s>(<%s>)' % (self.url, mytoken)
        etag = self.get_etag()
##         print 'upload: ETAG:', etag
        if etag:
            try:
                ifclause = hdrs['If']
                ifclause += '([%s])' % etag
            except KeyError:
                ifclause = '<%s>([%s])' % (self.url, etag)
                pass
            hdrs['If'] = ifclause
        res = self._conn.put(self.url, data,
                             content_type=mime_type,
                             content_enc=encoding,
                             extra_hdrs=hdrs)
        res = DAVResult(res)
        if res.status not in (200, 201, 204):
            raise DAVUploadFailedError, (res.status, res.reason)
        self.update()
        return
#

class DAVCollection ( DAVResource ):

    def __init__ ( self, url, conn=None, auto_request=False ):
        """Initialize a fresh DAVCollection instance.

        Call DAVResource.__init__ and checks if the url points to
        a collection. If the url does not point to a collection,
        DAVNoCollectionError is raised.
        """
        if url[-1] != '/':
            url += '/'
        DAVResource.__init__(self, url, conn, auto_request)
        if not self.is_collection():
            raise DAVNoCollectionError
        return

    def update ( self, conn=None, depth=1 ):
        return DAVResource.update(self, conn=conn, depth=depth)

    def get_child_names ( self ):
        """Return all children of this collection as absolute path names
        on this server.
        """
        ret = []
        if self.auto_request or not self._result:
            self.update()
        result = self._result
        for url, e in result.responses.items():
            if url == self.path:
                continue
            ret.append(url)
        return ret

    def get_child_objects ( self ):
        """Return all children of this collection as DAVResources.
        """
        ret = []
        if self.auto_request or not self._result:
            self.update()
        # for all (except ourself) responses get the href element
        # and create the appropiate instance for it
        result = self._result
        for url, e in result.responses.items():
            if url == self.path:
                continue
            if url == self.path:
                continue
            furl = self._make_url_for(url)
            try:
                fo = DAVFile(furl, self._conn, self.auto_request)
            except DAVNoFileError:
                fo = DAVCollection(furl, self._conn, self.auto_request)
                pass
            except DAVError, ex:
                if ex.args[0] in (403, 404, 405): # forbidden, not found, mehtod not allowed
                    # ignore files one does not have access to
                    continue
                raise
            ret.append(fo)
        return ret

    def _do_create_collection ( self, name, locktoken=None ):
        conn = self._conn
        # construct path
        while name and name[0] == '/':
            name = name[1:]
        if name[-1] != '/':
            name += '/'
        url  = urljoin(self.url, name )
        path = urlparse(url, 'http', 0)[2]
        res  = conn.mkcol(path)
        if res:
            res = DAVResult(res)
        return (res, url)

    def _do_create_file ( self, name, data='', content_type=None, encoding=None, locktoken=None ):
        conn = self._conn
        # construct path
        while name and name[0] == '/':
            name = name[1:]
        url  = urljoin(self.url, name)
        path = urlparse(url, 'http', 0)[2]
        # lock resource, should be ok even if the resource does not exist
        # but use provided lock token if given
        if locktoken is None:
            res = self._lock_path(path, owner=_DEFAULT_OWNER2, depth='0')
            if res.status not in (200, 201):
                raise DAVLockedError, (res.status, res.reason, url)
        mytoken = locktoken or res.lock_token
        try:
            # check if there is a resource with that name
            r = conn.head(url)
            r.read()
            if r.status != 404:
                # resource exists!
                raise DAVCreationFailedError, (r.status, r.reason, url)
            # resource does not exist, create file
            # headers needed to honor the lock
            hdr = { 'If': '<%s>(<%s>)' % (url, mytoken),
                    'Lock-Token': '<%s>' % mytoken }
            res = None
            res = conn.put(path, data,
                           content_type=content_type,
                           content_enc=encoding,
                           extra_hdrs=hdr)
            if res:
                res = DAVResult(res)
        finally:
            # unlock resource, even in case of exception
            # but only if we provided lock token
            if locktoken is None:
                self._unlock_path(path, mytoken)
        return (res, url)

    def create_collection ( self, name, locktoken=None ):
        """Create a new sub-collection as direct child of this collection.

        Path names like 'xxx/aaa' are not allowed and will result in an error.

        Returns a DAVCollection instance refering to the newly create collection.
        """
        res, url = self._do_create_collection(name, locktoken=locktoken)
        if res.status in (200, 201):
            # created, return collection
            return DAVCollection(url, self._conn)
        raise DAVCreationFailedError(res.status, res.reason, url)

    def create_file ( self, name, data='', content_type=None, locktoken=None ):
        """Create a new file as direct child of this collection.

        Path names like 'xxx/aaa' are not allowed and will result in an error.

        Returns a DAVFile instance refering to the newly created file.
        """
        res, url = self._do_create_file(name, data=data, content_type=content_type, locktoken=locktoken)
        if res.status in (200, 201):
            # created, return file
            self.update()
            return DAVFile(url, self._conn)
        raise DAVCreationFailedError, (res.status, res.reason, url)

    def _do_del ( self, url, path, locktoken=None ):
        # issue del request and hold result
        if locktoken: hdr = { 'If': _mk_if_data(url, mytoken) }
        else: hdr = {}
        return self._conn.delete(path, hdr)

    def delete ( self, name, locktoken=None ):
        """Delete a resource from this collection
        """
        # construct path
        while name and name[0] == '/':
            name = name[1:]
        url = urljoin(self.url, name)
        path = urlparse(url, 'http', 0)[2]
        # do delete
        res = self._do_del(url, path, locktoken=locktoken)
        res.read()
        if res.status == 423:
            raise DAVLockedError(res.status, res.reason, url)
        if res.status >= 300:
            raise DAVDeleteFailedError(res.status, res.reason, url)
        # deleted and done
        res.close()
        self.update()
        return
