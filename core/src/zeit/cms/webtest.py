from io import BytesIO
import six.moves.http_client
import six.moves.xmlrpc_client
import transaction
import webtest
import zope.component.hooks
import zope.security.management


def ServerProxy(uri, wsgi_app, encoding=None,
                verbose=0, allow_none=0, handleErrors=True):
    """A factory that creates a server proxy using the WebTestTransport
    by default.
    """
    transport = WebTestTransport(webtest.TestApp(wsgi_app), handleErrors)
    return six.moves.xmlrpc_client.ServerProxy(
        uri, transport, encoding, verbose, allow_none)


class WebTestTransport(six.moves.xmlrpc_client.Transport):
    """xmlrpclib transport that delegates to webtest.

    It can be used like a normal transport, including support for basic
    authentication.
    """

    verbose = False

    def __init__(self, testapp, handleErrors=True, use_datetime=0):
        six.moves.xmlrpc_client.Transport.__init__(
            self, use_datetime=use_datetime)
        self.testapp = testapp
        self.handleErrors = handleErrors

    def request(self, host, handler, request_body, verbose=0):
        # Like zeit.cms.testing.Browser
        transaction.commit()
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(None)
        old_interaction = zope.security.management.queryInteraction()
        zope.security.management.endInteraction()
        try:
            return self._request(host, handler, request_body, verbose)
        finally:
            zope.component.hooks.setSite(old_site)
            if old_interaction:
                zope.security.management.thread_local.interaction = (
                    old_interaction)

    def _request(self, host, handler, request_body, verbose=0):
        headers = {
            'Content-Length': str(len(request_body)),
            'Content-Type': 'text/xml',
        }
        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            headers['Authorization'] = dict(extra_headers)["Authorization"]

        extra_environ = {}
        if self.handleErrors:  # copied from zope.testbrowser
            extra_environ['paste.throw_errors'] = None
            headers['X-zope-handle-errors'] = 'True'
        else:
            extra_environ['wsgi.handleErrors'] = False
            extra_environ['paste.throw_errors'] = True
            extra_environ['x-wsgiorg.throw_errors'] = True
            headers.pop('X-zope-handle-errors', None)

        response = self.testapp.post(
            handler, request_body,
            headers=headers,
            extra_environ=extra_environ,
            expect_errors=True)

        errcode = response.status_int
        errmsg = response.status
        if errcode != 200:
            raise six.moves.xmlrpc_client.ProtocolError(
                host + handler,
                errcode, errmsg,
                response.headers)

        res = six.moves.http_client.HTTPResponse(FakeSocket(response.body))
        res.begin()
        return self.parse_response(res)


class FakeSocket:

    prefix = b'HTTP/1.1 200 Ok\r\n\r\n'

    def __init__(self, data):
        self.data = data

    def makefile(self, mode, bufsize=None):
        return BytesIO(self.prefix + self.data)
