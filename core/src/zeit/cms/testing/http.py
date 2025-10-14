import logging
import os
import threading

import gocept.httpserverlayer.custom
import waitress.server

from .layer import Layer


# Layer API modelled after gocept.httpserverlayer.wsgi
class WSGIServerLayer(Layer):
    port = 0  # choose automatically

    def __init__(self, bases=None):
        super().__init__(bases)
        self.wsgi_app = None

    @property
    def wsgi_app(self):
        return self.get('wsgi_app', self._wsgi_app)

    @wsgi_app.setter
    def wsgi_app(self, value):
        self._wsgi_app = value

    @property
    def host(self):
        return os.environ.get('GOCEPT_HTTP_APP_HOST', 'localhost')

    def setUp(self):
        self['httpd'] = waitress.server.create_server(
            self.wsgi_app, host=self.host, port=0, ipv6=False, clear_untrusted_proxy_headers=True
        )

        if isinstance(self['httpd'], waitress.server.MultiSocketServer):
            self['http_host'] = self['httpd'].effective_listen[0][0]
            self['http_port'] = self['httpd'].effective_listen[0][1]
        else:
            self['http_host'] = self['httpd'].effective_host
            self['http_port'] = self['httpd'].effective_port
        self['http_address'] = '%s:%s' % (self['http_host'], self['http_port'])

        self['httpd_thread'] = threading.Thread(target=self._run)
        self['httpd_thread'].daemon = True
        self['httpd_thread'].start()

    def _run(self):
        try:
            self['httpd'].run()
        except Exception:
            # Ignore "bad file descriptor" exceptions during tearDown
            logging.getLogger('waitress').warning(
                'Suppressed exception to keep thread from crashing'
                ' (most probably during shutdown anyway)',
                exc_info=True,
            )

    def tearDown(self):
        self['httpd'].close()

        self['httpd_thread'].join(5)
        if self['httpd_thread'].is_alive():
            raise RuntimeError('WSGI server could not be shut down')

        del self['httpd']
        del self['httpd_thread']

        del self['http_host']
        del self['http_port']
        del self['http_address']


class RecordingRequestHandler(gocept.httpserverlayer.custom.RequestHandler):
    @classmethod
    def reset(cls):
        cls.requests = []
        cls.response_headers = {}
        cls.response_body = '{}'
        cls.response_code = 200

    def do_GET(self):
        length = int(self.headers.get('content-length', 0))
        self.requests.append(
            {
                'verb': self.command,
                'path': self.path,
                'headers': self.headers,
                'body': self.rfile.read(length).decode('utf-8') if length else None,
            }
        )
        self.send_response(self._next('response_code'))
        for key, value in self._next('response_headers').items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(self._next('response_body').encode('utf-8'))

    def _next(self, name):
        result = getattr(self, name)
        if isinstance(result, list):
            result = result.pop(0)
        return result

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_PATCH = do_GET


class HTTPLayer(gocept.httpserverlayer.custom.Layer):
    def __init__(self, request_handler=RecordingRequestHandler):
        super().__init__(request_handler)
        if issubclass(request_handler, RecordingRequestHandler):
            request_handler.reset()

    def testSetUp(self):
        super().testSetUp()
        if issubclass(self['request_handler'], RecordingRequestHandler):
            self['request_handler'].reset()
