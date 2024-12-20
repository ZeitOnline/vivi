import logging
import os
import urllib.parse
import wsgiref.util

from opentelemetry.metrics import NoOpUpDownCounter
from opentelemetry.util.http import ExcludeList
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.authentication.interfaces import IUnauthenticatedPrincipal
import fanstatic
import grokcore.component as grok
import opentelemetry.instrumentation.wsgi
import opentelemetry.trace
import prometheus_client
import webob.cookies
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.app.wsgi
import zope.app.wsgi.paste
import zope.component
import zope.component.hooks
import zope.publisher.browser

from zeit.cms.tracing import anonymize
import zeit.cms.cli
import zeit.cms.interfaces
import zeit.cms.relstorage
import zeit.cms.tracing
import zeit.cms.wsgi
import zeit.cms.zope


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
        ('bugsnag', 'call:zeit.cms.bugsnag:bugsnag_filter'),
        ('prometheus', 'call:zeit.cms.application:prometheus_filter'),
        # fanstatic is confused by the SCRIPT_NAME that repoze.vhm sets, so
        # have it run first, before vhm applies any wsgi environ changes.
        ('fanstatic', 'call:fanstatic:make_fanstatic'),
        ('vhm', 'call:repoze.vhm.middleware:make_filter'),
    ]

    tracing_exclude = ['/@@health-check$', '/%40%40health-check$', '/metrics$']

    def __call__(self, global_conf=None, **local_conf):
        settings = local_conf
        settings.update(os.environ)
        zeit.cms.cli.configure(settings)
        log.info('Configuring ZCA')
        zeit.cms.zope.configure_product_config(settings)
        zeit.cms.zope.load_zcml(settings)
        db = zeit.cms.zope.DelayedInitZODB(settings['zodbconn.uri'])

        debug = zope.app.wsgi.paste.asbool(settings.get('debug'))
        app = zope.app.wsgi.WSGIPublisherApplication(
            db, HTTPPublicationRequestFactory, handle_errors=not debug
        )

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
        app = zeit.cms.wsgi.wsgi_pipeline(app, pipeline, settings)
        app = OpenTelemetryMiddleware(
            app,
            ExcludeList(self.tracing_exclude),
            request_hook=otel_request_hook,
            response_hook=otel_response_hook,
        )
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


grok.global_utility(BrowserRequest.factory, zope.app.publication.interfaces.IBrowserRequestFactory)


# Need to use a middleware so the URL can be exactly `/metrics`;
# Zope only would give us `/@@metrics`, and the legacy chef-based discovery
# does not support configuring the path, sigh.
class MetricsMiddleware:
    def __init__(self, wsgi):
        self.wsgi = wsgi
        registry = zope.component.getUtility(zeit.cms.interfaces.IPrometheusRegistry)
        self.metrics = prometheus_client.make_wsgi_app(registry)

    def __call__(self, environ, start_response):
        url = wsgiref.util.request_uri(environ)
        url = urllib.parse.urlparse(url)
        if url.path != '/metrics':
            return self.wsgi(environ, start_response)
        return self.metrics(environ, start_response)


def prometheus_filter(app, global_conf, **local_conf):
    return MetricsMiddleware(app)


class OpenTelemetryMiddleware(opentelemetry.instrumentation.wsgi.OpenTelemetryMiddleware):
    """Port excluded_urls feature from opentelemetry-instrumentation-asgi"""

    def __init__(self, wsgi, excluded_urls=None, *args, **kw):
        super().__init__(wsgi, *args, **kw)
        self.excluded_urls = excluded_urls
        # We're not interested (and Gauges cause bloat due to multiprocess)
        self.active_requests_counter = NoOpUpDownCounter('')

    def __call__(self, environ, start_response):
        url = wsgiref.util.request_uri(environ)
        if self.excluded_urls and self.excluded_urls.url_disabled(url):
            return self.wsgi(environ, start_response)
        return super().__call__(environ, start_response)


def otel_request_hook(span, environ):
    context = zeit.cms.tracing.apply_samplerate_productconfig(
        'zeit.cms.relstorage',
        'zeit.cms',
        'samplerate-zodb',
        opentelemetry.context.get_current(),
    )
    context = zeit.cms.tracing.apply_samplerate_productconfig(
        'zeit.connector.postgresql.tracing', 'zeit.cms', 'samplerate-sql', context
    )
    context = opentelemetry.context.set_value(
        # See opentelemetry.instrumentation.sqlcommenter_utils
        'SQLCOMMENTER_ORM_TAGS_AND_VALUES',
        {
            'application': 'vivi',
            'controller': 'web',
            # 'route':
            # 'action':
        },
        context,
    )
    environ['zeit.cms.tracing'] = opentelemetry.context.attach(context)

    clientip = environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
    span.set_attribute('net.peer.ip', anonymize(clientip))

    # Unfortunately, the otel API for Span is write-only, sigh.
    if getattr(span, 'attributes', None) is None:
        return
    path = span.attributes.get('http.target', '').split('/')
    if len(path) >= 3 and path[1] == 'workingcopy':
        path[2] = anonymize(path[2])
        span.set_attribute('http.target', '/'.join(path))


def otel_response_hook(span, environ, status, headers):
    token = environ.get('zeit.cms.tracing')
    if token is not None:
        opentelemetry.context.detach(token)


@grok.subscribe(zope.publisher.interfaces.IEndRequestEvent)
def add_username_to_span(event):
    principal = getattr(event.request, 'principal', None)
    if not principal or IUnauthenticatedPrincipal.providedBy(principal):
        return
    span = opentelemetry.trace.get_current_span()
    span.set_attribute('enduser.id', anonymize(principal.id))
