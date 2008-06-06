import base64
import httplib
import mimetypes
import re
import sys
import urllib
import urlparse

# This is for debugging, *NOT TO BE USED IN PRODUCTION*
DEBUG_REQUEST = False

XML_DOC_HEADER = '<?xml version="1.0" encoding="utf-8"?>'
XML_CONTENT_TYPE = 'text/xml; charset="utf-8"'


class BadAuthTypeError ( Exception ):
    pass

class RedirectError ( Exception ):
    pass


class HTTPBasicAuthCon:
    """Connection which authenticates.

    NOTE: currently doesn't authenticate.

    """

    connect_class = httplib.HTTPConnection
    rx = re.compile('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"')
    authhdr = 'WWW-Authenticate'

    def __init__ ( self, host, port=None, strict=None ):
        self._resp = None
        self._authon = False
        self._con = self.connect_class(host, port, strict)
        self._con.debuglevel = 0
        self._realms = {}
        self._user = ''
        self._passwd = ''
        self._realm = None
        return

    def set_auth ( self, user, passwd, realm=None ):
        if realm is None:
            self._user = user
            self._passwd = passwd
            self._authon = True
        else:
            self._realms[realm] = (user, passwd)
            self._authon = False
        return

    def get_auth ( self, realm ):
        try:
            u, p = self._realms[realm]
        except KeyError:
            u, p = self._user, self._passwd
            pass
        return (u, p)

    def _auth ( self, resp, headers ):
        # we need authentication
        resp.read()
        # do basic auth
        ah = resp.getheader(self.authhdr)
        resp.close()
        m = self.rx.match(ah)
        if m:
            scheme, realm = m.groups()
            if scheme.lower() != 'basic':
                raise BadAuthTypeError(scheme)
            # set basic auth header and retry
            raw = "%s:%s" % self.get_auth(realm)
            self._realm = realm
            auth = 'Basic %s' % base64.encodestring(raw).strip()
            headers['Authorization'] = auth
        return

    def request ( self, method, uri, body=None, headers={} ):
        #if self._resp is not None:
        #    self._resp.close()
        #    self._resp = None
        if self._authon:
            # short cut to avoid useless requests
            raw = "%s:%s" % self.get_auth(self._realm)
            auth = 'Basic %s' % base64.encodestring(raw).strip()
            headers['Authorization'] = auth
        ulist = list(urlparse.urlparse(uri))
        if ulist[1]:
            headers['Host'] = ulist[1]
        headers['Connection'] = 'keep-alive'
        # FIXME: after getting rid of .quote(): do we need unparse(parse(...))?
        # ulist[2] = urllib.quote(ulist[2])
        uri = urlparse.urlunparse(tuple(ulist))
        self._con.request(method, uri, body, headers)

    def getresponse(self):
        return self._con.getresponse()

    def close ( self ):
        if self._resp is not None:
            self._resp.close()
            self._resp = None
        self._con.close()
        return
#

class DAVBase:

    def get(self, url, extra_hdrs={ }):
        return self._request('GET', url, extra_hdrs=extra_hdrs)

    def head(self, url, extra_hdrs={ }):
        return self._request('HEAD', url, extra_hdrs=extra_hdrs)

    def post(self, url, data={ }, body=None, extra_hdrs={ }):
        headers = extra_hdrs.copy()
        assert body or data, "body or data must be supplied"
        assert not (body and data), "cannot supply both body and data"
        if data:
            body = ''
            for key, value in data.items():
                if isinstance(value, types.ListType):
                    for item in value:
                        body = body + '&' + key + '=' + urllib.quote(str(item))
                else:
                    body = body + '&' + key + '=' + urllib.quote(str(value))
            body = body[1:]
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return self._request('POST', url, body, headers)

    def options(self, url='*', extra_hdrs={ }):
        return self._request('OPTIONS', url, extra_hdrs=extra_hdrs)

    def trace(self, url, extra_hdrs={ }):
        return self._request('TRACE', url, extra_hdrs=extra_hdrs)

    def put(self, url, contents,
            content_type=None, content_enc=None, extra_hdrs={ }):
        if not content_type:
            content_type, content_enc = mimetypes.guess_type(url)
        headers = extra_hdrs.copy()
        if content_type:
            headers['Content-Type'] = content_type
        if content_enc:
            headers['Content-Encoding'] = content_enc
        return self._request('PUT', url, contents, headers)

    def delete(self, url, extra_hdrs={ }):
        return self._request('DELETE', url, extra_hdrs=extra_hdrs)

    def propfind(self, url, body=None, depth=None, extra_hdrs={ }):
        headers = extra_hdrs.copy()
        headers['Content-Type'] = XML_CONTENT_TYPE
        if depth is not None:
            headers['Depth'] = str(depth)
        else:
            headers['Depth'] = '0'
        ret = self._request('PROPFIND', url, body, headers)
        return ret

    def search(self, url, body=None, extra_hdrs={}):
        return self._request('SEARCH', url, body, extra_hdrs=extra_hdrs)

    def proppatch(self, url, body, extra_hdrs={ }):
        headers = extra_hdrs.copy()
        headers['Content-Type'] = XML_CONTENT_TYPE
        ret = self._request('PROPPATCH', url, body, headers)
        return ret

    def mkcol(self, url, hdrs={ }):
        return self._request('MKCOL', url, extra_hdrs=hdrs)

    def move(self, src, dst, extra_hdrs={ }):
        headers = extra_hdrs.copy()
        headers['Destination'] = dst
        return self._request('MOVE', src, extra_hdrs=headers)

    def copy(self, src, dst, depth=None, extra_hdrs={ }):
        headers = extra_hdrs.copy()
        headers['Destination'] = dst
        if depth is not None:
            headers['Depth'] = str(depth)
        return self._request('COPY', src, extra_hdrs=headers)

    def lock(self, url, owner='', timeout=None, depth=None,
             scope='exclusive', type='write', extra_hdrs={ }):
        headers = extra_hdrs.copy()
        headers['Content-Type'] = XML_CONTENT_TYPE
        headers['Host'] = self._con.host
        if depth is not None:
            headers['Depth'] = str(depth)
        if timeout is None:
            headers['Timeout'] = 'Infinite'
        else:
            headers['Timeout'] = 'Second-%d' % timeout
        #:fixme: Here we should use ElementTree to construct a
        # proper XML request body
        body = [XML_DOC_HEADER,
               '<DAV:lockinfo xmlns:DAV="DAV:">',
               '<DAV:lockscope><DAV:%s/></DAV:lockscope>' % scope,
               '<DAV:locktype><DAV:%s/></DAV:locktype>' % type]
        if owner:
            body.append('<DAV:owner>%s</DAV:owner>\n' % owner)
        body.append('</DAV:lockinfo>')
        return self._request('LOCK', url, ''.join(body), extra_hdrs=headers)

    def unlock(self, url, locktoken, extra_hdrs=None):
        if extra_hdrs is None:
            extra_hdrs = {}
        headers = extra_hdrs.copy()
        if not locktoken:
            return None
        if locktoken[0] != '<':
            locktoken = '<' + locktoken + '>'
        headers['Lock-Token'] = locktoken
##         headers['If'] = '(' + locktoken + ')'
        return self._request('UNLOCK', url, extra_hdrs=headers)

    def _request(self, method, url, body=None, extra_hdrs={}):
        "Internal method for sending a request."
        self._recursion_level = getattr(self, '_recursion_level', 0) + 1
        if DEBUG_REQUEST:
            print >>sys.stderr, (
                "### REQUEST:  ###\n  %s %s\n  %s\n\n  %s\n############\n" % (
                    method, url,
                    "\n  ".join(["%s: %s" % (k, v) for k, v in extra_hdrs.items()]),
                    body))
        self.request(method, url, body, extra_hdrs) # that's HTTPxxxAuthCon.request, called via DAVConnection
        resp = self.getresponse()
        if DEBUG_REQUEST:
            print >>sys.stderr, (
                "### RESPONSE: ###\n  %s %s\n  %s\n#################\n" % (
                    (resp.status, resp.reason,
                     "\n  ".join(["%s: %s" % h for h in resp.getheaders()]))))
        if resp.status in (301, 302, 303, 305, 307):
            # redirect silently
            # Location: header *MUST* be there
            new_uri = resp.msg['Location']
            # RECURSION AHEAD !
            if self._recursion_level > 10:
                # do NOT descend further, return last response
                return resp
            resp.read()
            #resp.close()
            resp = self._request(method, new_uri, body, extra_hdrs)
        self._recursion_level -= 1
        return resp
#


class DAVConnection ( HTTPBasicAuthCon, DAVBase ):

    def __init__ ( self, host, port=None, strict=None):
        HTTPBasicAuthCon.__init__(self, host, port, strict)
        self._con._http_vsn_str = 'HTTP/1.1'
        self._con._http_vsn = 11
        return
#

import socket
if getattr(socket, 'ssl', None):
    # only include DAVS if SSL support is compiled in
    class HTTPSBasicAuthCon ( HTTPBasicAuthCon ):
        connect_class = httplib.HTTPSConnection
        pass
    #

    class DAVSConnection ( HTTPSBasicAuthCon, DAVBase):
        def __init__ ( self, host, port=None, strict=None):
            HTTPSBasicAuthCon.__init__(self, host, port, strict)
            self._con._http_vsn_str = 'HTTP/1.1'
            self._con._http_vsn = 11
            return
    #
###
