import base64
import http.client
import importlib.metadata
import logging
import mimetypes
import re
import socket
import sys
import urllib.parse

from opentelemetry.instrumentation.utils import http_status_to_status_code
from opentelemetry.trace.status import Status
import lxml.etree
import zope.component

import zeit.cms.interfaces
import zeit.cms.tracing


# This is for debugging, *NOT TO BE USED IN PRODUCTION*
DEBUG_REQUEST = False
DEBUG_CONNECTION = False

XML_CONTENT_TYPE = 'text/xml; charset="utf-8"'
try:
    USER_AGENT = 'zeit.connector/' + importlib.metadata.version('vivi.core')
except Exception:
    USER_AGENT = 'zeit.connector/unknown'

logger = logging.getLogger(__name__)


class BadAuthTypeError(Exception):
    pass


class HTTPBasicAuthCon:
    """Connection which authenticates.

    NOTE: currently doesn't authenticate.

    """

    connect_class = http.client.HTTPConnection
    rx = re.compile('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"')
    authhdr = 'WWW-Authenticate'

    def __init__(self, host, port=None, strict=None):
        self._resp = None
        self._authon = False
        self._host = host
        self._port = port
        self._strict = strict
        self._realms = {}
        self._user = ''
        self._passwd = ''  # noqa
        self._realm = None
        self.additional_headers = {}
        # Actually connect
        self.connect()

    def connect(self):
        self._con = self.connect_class(self._host, self._port, self._strict)
        if DEBUG_CONNECTION:
            self._con.debuglevel = 1

    def set_auth(self, user, passwd, realm=None):
        if realm is None:
            self._user = user
            self._passwd = passwd
            self._authon = True
        else:
            self._realms[realm] = (user, passwd)
            self._authon = False
        return

    def get_auth(self, realm):
        try:
            u, p = self._realms[realm]
        except KeyError:
            u, p = self._user, self._passwd
            pass
        return (u, p)

    def _auth(self, resp, headers):
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
            raw = '%s:%s' % self.get_auth(realm)
            self._realm = realm
            auth = 'Basic %s' % base64.encodestring(raw).strip()
            headers['Authorization'] = auth
        return

    def get_quoted_path(self, uri):
        path = urllib.parse.urlunparse(('', '') + urllib.parse.urlparse(uri)[2:])
        # NOTE: Everything after the netloc is considered a path and will be
        # quoted
        quoted = urllib.parse.quote(path)
        return quoted

    def quote_uri(self, uri):
        parsed = urllib.parse.urlparse(uri)
        quoted = urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, self.get_quoted_path(uri), '', '', '')
        )
        return quoted

    def request(self, method, uri, body=None, extra_hdrs=None):
        path = self.get_quoted_path(uri)
        uri = self.quote_uri(uri)
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        if self._resp is not None and not self._resp.isclosed():
            raise AssertionError('Response left')
        if self._authon:
            # short cut to avoid useless requests
            raw = '%s:%s' % self.get_auth(self._realm)
            auth = 'Basic %s' % base64.encodestring(raw).strip()
            headers['Authorization'] = auth
        host = str(urllib.parse.urlparse(uri).netloc)
        if host:
            headers['Host'] = host
        headers['Connection'] = 'keep-alive'
        headers['User-Agent'] = USER_AGENT
        headers.update(self.additional_headers)
        try:
            self._con.request(method, path, body, headers)
        except http.client.CannotSendRequest:
            # Yikes. The connection got into an inconsistent state! Reconnect.
            self.connect()
            # If that raises the error again, well let it raise.
            self._con.request(method, uri, body, headers)

    def getresponse(self):
        self._resp = self._con.getresponse()
        return self._resp

    def close(self):
        if self._resp is not None:
            self._resp.close()
            self._resp = None
        self._con.close()
        return


class DAVBase:
    def get(self, url, extra_hdrs=None):
        return self._request('GET', url, extra_hdrs=extra_hdrs)

    def head(self, url, extra_hdrs=None):
        return self._request('HEAD', url, extra_hdrs=extra_hdrs)

    def post(self, url, data=None, body=None, extra_hdrs=None):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        assert body or data, 'body or data must be supplied'
        assert not (body and data), 'cannot supply both body and data'
        if data:
            body = ''
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        body = body + '&' + key + '=' + urllib.parse.quote(str(item))
                else:
                    body = body + '&' + key + '=' + urllib.parse.quote(str(value))
            body = body[1:]
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return self._request('POST', url, body, headers)

    def options(self, url='*', extra_hdrs=None):
        return self._request('OPTIONS', url, extra_hdrs=extra_hdrs)

    def trace(self, url, extra_hdrs=None):
        return self._request('TRACE', url, extra_hdrs=extra_hdrs)

    def put(self, url, contents, content_type=None, content_enc=None, extra_hdrs=None):
        if not content_type:
            content_type, content_enc = mimetypes.guess_type(url)
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        if content_type:
            headers['Content-Type'] = content_type
        if content_enc:
            headers['Content-Encoding'] = content_enc
        return self._request('PUT', url, contents, headers)

    def delete(self, url, extra_hdrs=None):
        return self._request('DELETE', url, extra_hdrs=extra_hdrs)

    def propfind(self, url, body=None, depth=None, extra_hdrs=None):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        headers['Content-Type'] = XML_CONTENT_TYPE
        if depth is not None:
            headers['Depth'] = str(depth)
        else:
            headers['Depth'] = '0'
        ret = self._request('PROPFIND', url, body, headers)
        return ret

    def search(self, url, body=None, extra_hdrs=None):
        return self._request('SEARCH', url, body, extra_hdrs=extra_hdrs)

    def proppatch(self, url, body, extra_hdrs=None):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        headers['Content-Type'] = XML_CONTENT_TYPE
        ret = self._request('PROPPATCH', url, body, headers)
        return ret

    def mkcol(self, url, hdrs=None):
        return self._request('MKCOL', url, extra_hdrs=hdrs)

    def move(self, src, dst, extra_hdrs=None):
        headers = {}
        dst = self.quote_uri(dst)
        if extra_hdrs:
            headers.update(extra_hdrs)
        headers['Destination'] = dst
        return self._request('MOVE', src, extra_hdrs=headers)

    def copy(self, src, dst, depth=None, extra_hdrs=None):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        headers['Destination'] = self.quote_uri(dst)
        if depth is not None:
            headers['Depth'] = str(depth)
        return self._request('COPY', src, extra_hdrs=headers)

    def lock(
        self,
        url,
        owner='',
        timeout=None,
        depth=None,
        scope='exclusive',
        type='write',
        extra_hdrs=None,
    ):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        headers['Content-Type'] = XML_CONTENT_TYPE
        headers['Host'] = self._con.host
        if depth is not None:
            headers['Depth'] = str(depth)
        if timeout is None:
            headers['Timeout'] = 'Infinite'
        else:
            headers['Timeout'] = 'Second-%d' % timeout
        body = lxml.etree.Element('{DAV:}lockinfo')
        node = lxml.etree.Element('{DAV:}lockscope')
        node.append(lxml.etree.Element('{DAV:}%s' % scope))
        body.append(node)
        node = lxml.etree.Element('{DAV:}locktype')
        node.append(lxml.etree.Element('{DAV:}%s' % type))
        body.append(node)
        if owner:
            node = lxml.etree.Element('{DAV:}owner')
            node.text = owner
            body.append(node)
        xmlstr = lxml.etree.tostring(body, encoding='UTF-8', xml_declaration=True)
        return self._request('LOCK', url, xmlstr, extra_hdrs=headers)

    def unlock(self, url, locktoken, extra_hdrs=None):
        headers = {}
        if extra_hdrs:
            headers.update(extra_hdrs)
        if not locktoken:
            return None
        if locktoken[0] != '<':
            locktoken = '<' + locktoken + '>'
        headers['Lock-Token'] = locktoken
        return self._request('UNLOCK', url, extra_hdrs=headers)

    def _request(self, method, url, body=None, extra_hdrs=None):
        "Internal method for sending a request."
        if DEBUG_REQUEST:
            if extra_hdrs:
                debug_header_items = ['%s: %s' % (k, v) for k, v in extra_hdrs.items()]
            else:
                debug_header_items = []
            sys.stderr.write(
                '### REQUEST:  ###\n  %s %s\n  %s\n\n  %s\n############\n'
                % (method, url, '\n  '.join(debug_header_items), body)
            )
        # that's HTTPxxxAuthCon.request, called via DAVConnection
        logger.debug('%s %s', method, url)
        tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
        with tracer.start_as_current_span(
            'DAV %s' % method, attributes={'http.url': url, 'http.method': method}
        ) as span:
            self.request(method, url, body, extra_hdrs)
            try:
                resp = self.getresponse()
            except http.client.BadStatusLine:
                # Gnah. We may have waited too long.  Try one more time.
                self.connect()
                self.request(method, url, body, extra_hdrs)
                resp = self.getresponse()
            span.set_attribute('http.status_code', resp.status)
            span.set_status(Status(http_status_to_status_code(resp.status)))

        if DEBUG_REQUEST:
            sys.stderr.write(
                '### RESPONSE: ###\n  %s %s\n  %s\n#################\n'
                % (
                    (
                        resp.status,
                        resp.reason,
                        '\n  '.join(['%s: %s' % h for h in resp.getheaders()]),
                    )
                )
            )
        return resp


class DAVConnection(HTTPBasicAuthCon, DAVBase):
    def __init__(self, host, port=None, strict=None, referrer=None):
        HTTPBasicAuthCon.__init__(self, host, port, strict)
        self._con._http_vsn_str = 'HTTP/1.1'
        self._con._http_vsn = 11
        return


if getattr(socket, 'ssl', None):
    # only include DAVS if SSL support is compiled in
    class HTTPSBasicAuthCon(HTTPBasicAuthCon):
        connect_class = http.client.HTTPSConnection
        pass

    class DAVSConnection(HTTPSBasicAuthCon, DAVBase):
        def __init__(self, host, port=None, strict=None):
            HTTPSBasicAuthCon.__init__(self, host, port, strict)
            self._con._http_vsn_str = 'HTTP/1.1'
            self._con._http_vsn = 11
            return
