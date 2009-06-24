import random
import time
import zeit.connector.dav.davbase
import zeit.connector.dav.davresource
import zeit.connector.dav.interfaces

class DAVConnection(zeit.connector.dav.davbase.DAVConnection):
    """DAV Connection oriented.

    (as opposed to resource oriented)
    """

    def lock(self, url, owner=None, depth=0, timeout=None, headers={}):
        r = self.get_result(
            'lock', url, owner=owner, depth=depth, timeout=timeout,
            extra_hdrs=headers)
        if not r.has_errors():
            return r.lock_token
        if r.status == 423:
            raise zeit.connector.dav.interfaces.DAVLockedError(r)
        raise zeit.connector.dav.interfaces.DAVLockFailedError(r)

    def unlock(self, url, locktoken, headers={}):
        if not locktoken:
            raise zeit.connector.dav.interfaces.DAVInvalidLocktokenError()
        r = self.get_result('unlock', url, locktoken, extra_hdrs=headers)
        if r.has_errors():
            raise zeit.connector.dav.interfaces.DAVUnlockFailedError(r)

    def propfind(self, *args, **kwargs):
        tries = 0
        while True:
            tries += 1
            try:
                return self.get_result('propfind', *args, **kwargs)
            except zeit.connector.dav.interfaces.DavXmlParseError, e:
                last_error = e.args[0].last_error
                if (last_error
                    and last_error.type_name == 'ERR_TAG_NOT_FINISHED'
                    and tries < 3):
                    # When we got incomplete data, wait a bit and try again.
                    time.sleep(random.uniform(0, 2**tries))
                    continue
                raise

    def proppatch(self, uri, body, locktoken=None):
        hdrs = {}
        self.set_if_header(hdrs, uri, locktoken)
        res = self.get_result('proppatch', uri, body, extra_hdrs=hdrs)
        if res.status == 200 or res.status >= 300:
            raise zeit.connector.dav.interfaces.DAVError(
                res.status, res.reason, res)
        return res

    def put(self, url, data, mime_type=None, encoding=None, locktoken=None,
            etag=None):
        if mime_type is None:
            mime_type = 'application/octet-stream'
        hdrs = {}
        self.set_if_header(hdrs, url, locktoken, etag)
        res = self.get_result(
            'put', url, data,
            content_type=mime_type, content_enc=encoding, extra_hdrs=hdrs)
        if res.status not in (200, 201, 204):
            raise zeit.connector.dav.interfaces.DAVUploadFailedError(
                res.status, res.reason)
        return res

    def delete(self, url, locktoken=None):
        hdrs = {}
        self.set_if_header(hdrs, url, locktoken)
        res = self.get_result('delete', url, hdrs)
        if res.status == 423:
            raise zeit.connector.dav.interfaces.DAVLockedError(
                res.status, res.reason, url)
        if res.status >= 300:
            raise zeit.connector.dav.interfaces.DAVDeleteFailedError(
                res.status, res.reason, url)
        return res

    def set_if_header(self, hdrs, url, locktoken=None, etag=None):
        if_clause = []
        if locktoken:
            hdrs['Lock-Token'] = '<%s>' % locktoken
            if_clause.append('(<%s>)' % locktoken)
        if etag:
            if_clause.append('([%s])' % etag)
        if if_clause:
            hdrs['If'] = '<%s>%s' % (self.quote_uri(url), ''.join(if_clause))

    def get_result(self, method_name, *args, **kwargs):
        method = getattr(super(DAVConnection, self), method_name)
        response = method(*args, **kwargs)
        return zeit.connector.dav.davresource.DAVResult(response)
