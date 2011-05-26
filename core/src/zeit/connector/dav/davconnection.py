import httplib
import random
import time
import zeit.connector.dav.davbase
import zeit.connector.dav.davresource
import zeit.connector.dav.interfaces


class DAVConnection(zeit.connector.dav.davbase.DAVConnection):
    """DAV Connection oriented.

    (as opposed to resource oriented)
    """

    error_map = {
        httplib.LOCKED:
            zeit.connector.dav.interfaces.DAVLockedError,
        httplib.PRECONDITION_FAILED:
            zeit.connector.dav.interfaces.PreconditionFailedError,
        httplib.MOVED_PERMANENTLY:
            zeit.connector.dav.interfaces.DAVRedirectError,
        httplib.NOT_FOUND:
            zeit.connector.dav.interfaces.DAVNotFoundError,
    }

    def lock(self, url, owner=None, depth=0, timeout=None, headers={}):
        r = self.get_result(
            'lock', (httplib.OK,),
            url, owner=owner, depth=depth, timeout=timeout,
            extra_hdrs=headers)
        return r.lock_token

    def unlock(self, url, locktoken, headers={}):
        r = self.get_result(
            'unlock', (httplib.NO_CONTENT,),
            url, locktoken, extra_hdrs=headers)
        return r

    def propfind(self, *args, **kwargs):
        tries = 0
        while True:
            tries += 1
            try:
                return self.get_result(
                    'propfind', (httplib.MULTI_STATUS,),
                    *args, **kwargs)
            except zeit.connector.dav.interfaces.DavXmlParseError, e:
                last_error = e.args[0].last_error
                if (last_error
                    and last_error.type_name == 'ERR_TAG_NOT_FINISHED'
                    and tries < 3):
                    # When we got incomplete data, wait a bit and try again.
                    time.sleep(random.uniform(0, 2**tries))
                    continue
                raise

    def proppatch(self, url, body, locktoken=None):
        hdrs = {}
        self.set_if_header(hdrs, url, locktoken)
        res = self.get_result(
            'proppatch', (httplib.MULTI_STATUS,),
            url, body, extra_hdrs=hdrs)
        return res

    def put(self, url, data, mime_type=None, encoding=None, locktoken=None,
            etag=None, extra_headers=None):
        if mime_type is None:
            mime_type = 'application/octet-stream'
        if extra_headers is None:
            extra_headers = {}
        self.set_if_header(extra_headers, url, locktoken, etag)
        res = self.get_result(
            'put', (httplib.OK, httplib.CREATED, httplib.NO_CONTENT),
            url, data, content_type=mime_type, content_enc=encoding,
            extra_hdrs=extra_headers)
        return res

    def mkcol(self, url):
        return self.get_result('mkcol', (httplib.CREATED,), url)

    def delete(self, url, locktoken=None):
        hdrs = {}
        self.set_if_header(hdrs, url, locktoken)
        res = self.get_result(
            'delete', (httplib.OK, httplib.ACCEPTED, httplib.NO_CONTENT),
            url, hdrs)
        return res

    def move(self, src, dst, extra_headers=None):
        res = self.get_result(
            'move', None, src, dst, extra_headers)
        return res

    def copy(self, src, dst, extra_headers=None):
        res = self.get_result(
            'copy', None, src, dst, extra_headers)
        return res

    def set_if_header(self, hdrs, url, locktoken=None, etag=None):
        if_clause = []
        if locktoken:
            if_clause.append('<%s>' % locktoken)
        if etag:
            if_clause.append('[%s]' % etag)
        if if_clause:
            hdrs['If'] = '<%s>(%s)' % (self.quote_uri(url), ''.join(if_clause))

    def get_result(self, method_name, accept_status, url,
                   *args, **kwargs):
        __traceback_info__ = (method_name, url)
        method = getattr(super(DAVConnection, self), method_name)
        response = method(url, *args, **kwargs)
        if accept_status is None or response.status in accept_status:
            return zeit.connector.dav.davresource.DAVResult(response)
        body = response.read()
        exception = self.error_map.get(response.status)
        if exception is None:
            raise httplib.HTTPException(
                response.status, response.reason, url, body, response)
        raise exception(response.status, response.reason, url, body, response)
