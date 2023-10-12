from opentelemetry.util.http import ExcludeList
from zeit.cms.tracing import anonymize
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.authentication.interfaces import IUnauthenticatedPrincipal
import fanstatic
import grokcore.component as grok
import logging
import opentelemetry.instrumentation.wsgi
import opentelemetry.trace
import os
import webob.cookies
import wsgiref.util
import zeit.cms.cli
import zeit.cms.wsgi
import zeit.cms.zeo
import zeit.cms.zope
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.app.wsgi
import zope.app.wsgi.paste
import zope.component.hooks
import zope.publisher.browser


log = logging.getLogger(__name__)


FANSTATIC_SETTINGS = {
    'bottom': True,
    'bundle': not os.environ.get('FANSTATIC_DEBUG', False),
    'minified': False,  # XXX
    'compile': True,
    'versioning': os.environ.get('FANSTATIC_VERSIONING', True),
    'versioning_use_md5': True,
    # Once on startup, not every request
    'recompute_hashes': False,
    'publisher_signature': fanstatic.DEFAULT_SIGNATURE,
}


class Application:

    pipeline = [
        ('slowlog', 'egg:slowlog#slowlog'),
        ('bugsnag', 'egg:vivi.core#bugsnag'),
        # fanstatic is confused by the SCRIPT_NAME that repoze.vhm sets, so
        # have it run first, before vhm applies any wsgi environ changes.
        ('fanstatic', 'egg:fanstatic#fanstatic'),
        ('vhm', 'egg:repoze.vhm#vhm_xheaders'),
    ]

    def __call__(self, global_conf=None, **local_conf):
        settings = os.environ.copy()
        settings.update(local_conf)
        zeit.cms.cli.configure(settings)
        log.info('Configuring ZCA')
        zeit.cms.zope.configure_product_config(settings)
        zeit.cms.zope.load_zcml(settings)
        db = zeit.cms.zope.DelayedInitZODB(settings['zodbconn.uri'])

        debug = zope.app.wsgi.paste.asbool(settings.get('debug'))
        app = zope.app.wsgi.WSGIPublisherApplication(
            db, HTTPPublicationRequestFactory, handle_errors=not debug)

        for key, value in FANSTATIC_SETTINGS.items():
            settings['fanstatic.' + key] = value

        log.info('Configuring WSGI')
        pipeline = self.pipeline
        if debug:
            settings['debugger.evalex'] = True
            pipeline = [
                ('dbfanstatic', 'call:zeit.cms.application:clear_fanstatic'),
                ('debugger', 'call:zeit.cms.application:werkzeug_debugger'),
            ] + pipeline
        if settings.get('use_linesman'):
            pipeline = [
                ('linesman', 'egg:linesman#profiler'),
            ] + pipeline
        app = zeit.cms.wsgi.wsgi_pipeline(app, pipeline, settings)
        app = OpenTelemetryMiddleware(
            app, ExcludeList(['/@@health-check$']),
            request_hook=otel_request_hook)
        return app


APPLICATION = Application()


def werkzeug_debugger(app, global_conf, **local_conf):
    import werkzeug.debug
    return werkzeug.debug.DebuggedApplication(app, **local_conf)


class ClearFanstaticOnError:
    """In debug mode, removes any application CSS on error, so as not to clash
    with the CSS of werkzeug debugger.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception:
            fanstatic.clear_needed()
            raise


def clear_fanstatic(app, global_conf, **local_conf):
    return ClearFanstaticOnError(app)


class BrowserRequest(zope.publisher.browser.BrowserRequest):

    def _HTTPRequest__deduceServerURL(self):
        if self._environ.get('wsgi.url_scheme') == 'https':  # See repoze.vhm
            self._environ['SERVER_PORT_SECURE'] = '1'
        return super()._HTTPRequest__deduceServerURL()

    def _parseCookies(self, text, result=None):
        """Upstream uses python stdlib SimpleCookie, which returns a completely
        empty result when one cookie contains a non-ASCII character.
        """
        if result is None:
            result = {}
        cookies = webob.cookies.RequestCookies({'HTTP_COOKIE': text})
        result.update(cookies)
        return result

    @classmethod
    def factory(cls):
        return cls


grok.global_utility(
    BrowserRequest.factory,
    zope.app.publication.interfaces.IBrowserRequestFactory)


class OpenTelemetryMiddleware(
        opentelemetry.instrumentation.wsgi.OpenTelemetryMiddleware):
    """Port excluded_urls feature from opentelemetry-instrumentation-asgi"""

    def __init__(self, wsgi, excluded_urls=None, *args, **kw):
        super().__init__(wsgi, *args, **kw)
        self.excluded_urls = excluded_urls

    def __call__(self, environ, start_response):
        url = wsgiref.util.request_uri(environ)
        if self.excluded_urls and self.excluded_urls.url_disabled(url):
            return self.wsgi(environ, start_response)
        return super().__call__(environ, start_response)


def otel_request_hook(span, environ):
    zeit.cms.zeo.apply_samplerate(span, environ)
    clientip = environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
    span.set_attribute('net.peer.ip', anonymize(clientip))

    # Unfortunately, the otel API for Span is write-only, sigh.
    if getattr(span, 'attributes', None) is None:
        return
    path = span.attributes.get('http.target', '').split('/')
    if len(path) >= 3 and path[1] == 'workingcopy':
        path[2] = anonymize(path[2])
        span.set_attribute('http.target', '/'.join(path))


@grok.subscribe(zope.publisher.interfaces.IEndRequestEvent)
def add_username_to_span(event):
    principal = getattr(event.request, 'principal', None)
    if not principal or IUnauthenticatedPrincipal.providedBy(principal):
        return
    span = opentelemetry.trace.get_current_span()
    span.set_attribute('enduser.id', anonymize(principal.id))
