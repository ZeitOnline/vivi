from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
import fanstatic
import grokcore.component as grok
import os
import webob.cookies
import zeit.cms.cli
import zeit.cms.wsgi
import zeit.cms.zope
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.app.wsgi
import zope.app.wsgi.paste
import zope.component.hooks
import zope.publisher.browser


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

    def __call__(self, global_conf, **local_conf):
        settings = os.environ.copy()
        settings.update(local_conf)
        zeit.cms.cli.configure(settings)
        db = zeit.cms.zope.bootstrap(settings)

        debug = zope.app.wsgi.paste.asbool(settings.get('debug'))
        app = zope.app.wsgi.WSGIPublisherApplication(
            db, HTTPPublicationRequestFactory, handle_errors=not debug)

        for key, value in FANSTATIC_SETTINGS.items():
            settings['fanstatic.' + key] = value

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
        return zeit.cms.wsgi.wsgi_pipeline(app, pipeline, settings)


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
