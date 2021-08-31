from configparser import ConfigParser
import bugsnag
import bugsnag.wsgi
import bugsnag.wsgi.middleware
import fanstatic
import grokcore.component as grok
import logging.config
import os
import pendulum
import pkg_resources
import pyramid_dogpile_cache2
import re
import sys
import webob
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.app.wsgi
import zope.app.wsgi.paste
import zope.component.hooks
import zope.publisher.browser
import zope.security.checker


FANSTATIC_PATH = fanstatic.DEFAULT_SIGNATURE
FANSTATIC_DEBUG = os.environ.get('FANSTATIC_DEBUG', False)
FANSTATIC_VERSIONING = os.environ.get('FANSTATIC_VERSIONING', True)
BUNDLE = not FANSTATIC_DEBUG
MINIFIED = False  # XXX


# Make pendulum a rock, just like datetime.datetime.
for cls in ['DateTime', 'Date', 'Time']:
    zope.security.checker.BasicTypes[getattr(pendulum, cls)] = (
        zope.security.checker.NoProxy)


class Application:

    def __init__(self):
        self.pipeline = [
            # fanstatic is confused by the SCRIPT_NAME that repoze.vhm sets, so
            # repoze.vhm needs to come before fanstatic to keep them apart.
            ('repoze.vhm', 'paste.filter_app_factory', 'vhm_xheaders', {}),
            ('fanstatic', 'paste.filter_app_factory', 'fanstatic', {
                'bottom': True,
                'bundle': BUNDLE,
                'minified': MINIFIED,
                'compile': True,
                'versioning': FANSTATIC_VERSIONING,
                'versioning_use_md5': True,
                # Once on startup, not every request
                'recompute_hashes': False,
                'publisher_signature': FANSTATIC_PATH,
            }),
        ]

    def __call__(self, global_conf, **local_conf):
        debug = zope.app.wsgi.paste.asbool(local_conf.get('debug'))
        app = zope.app.wsgi.getWSGIApplication(
            local_conf['zope_conf'], handle_errors=not debug)
        if debug:
            import werkzeug.debug
            self.pipeline.insert(
                0, (werkzeug.debug.DebuggedApplication, 'factory', '', {
                    'evalex': True}))
            self.pipeline.insert(0, (ClearFanstaticOnError, 'factory', '', {}))
        return self.setup_pipeline(app, global_conf)

    def setup_pipeline(self, app, global_conf=None):
        for spec, protocol, name, extra in self.pipeline:
            if protocol == 'factory':
                app = spec(app, **extra)
                continue
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_conf, **extra)
        return app


APPLICATION = Application()


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


def zope_shell():
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s paste.ini\n' % sys.argv[0])
        sys.exit(1)
    paste_ini = sys.argv[1]
    logging.config.fileConfig(
        paste_ini, {'__file__': paste_ini, 'here': os.path.abspath(
            os.path.dirname(paste_ini))})
    config = ConfigParser()
    config.read(paste_ini)
    # XXX How to get to zope.conf is the only-application specific part.
    db = zope.app.wsgi.config(config.get('application:cms', 'zope_conf'))
    # Adapted from zc.zope3recipes.debugzope.debug()
    globs = {
        '__name__': '__main__',
        # Not really worth using zope.app.publication.ZopePublication.root_name
        'root': db.open().root()['Application'],
        'zeit': sys.modules['zeit'],
        'zope': sys.modules['zope'],
        'transaction': sys.modules['transaction'],
    }
    if len(sys.argv) > 2:
        sys.argv[:] = sys.argv[2:]
        globs['__file__'] = sys.argv[0]
        exec(compile(open(sys.argv[0], "rb").read(), sys.argv[0], 'exec'),
             globs)
        sys.exit()
    else:
        zope.component.hooks.setSite(globs['root'])
        import code
        # Modeled after pyramid.scripts.pshell
        code.interact(local=globs, banner="""\
Python %s on %s
Type "help" for more information.

Environment:
  root         ZODB application root folder (already set as ZCA site)
Modules that were pre-imported for convenience: zope, zeit, transaction
""" % (sys.version, sys.platform))


@grok.subscribe(zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
def configure_dogpile_cache(event):
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    settings = {
        'dogpile_cache.regions': config['cache-regions']
    }
    for region in re.split(r'\s*,\s*', config['cache-regions']):
        settings['dogpile_cache.%s.backend' % region] = 'dogpile.cache.memory'
        settings['dogpile_cache.%s.expiration_time' % region] = config[
            'cache-expiration-%s' % region]
    pyramid_dogpile_cache2.configure_dogpile_cache(settings)


class BugsnagMiddleware:

    def __init__(self, application):
        bugsnag.before_notify(add_wsgi_request_data_to_notification)
        self.application = application

    def __call__(self, environ, start_response):
        return bugsnag.wsgi.middleware.WrappedWSGIApp(
            self.application, environ, start_response)


# XXX copy&paste to remove overwriting the user id with the IP address
def add_wsgi_request_data_to_notification(notification):
    if not hasattr(notification.request_config, "wsgi_environ"):
        return

    environ = notification.request_config.wsgi_environ
    request = webob.Request(environ)

    notification.context = "%s %s" % (
        request.method, bugsnag.wsgi.request_path(environ))
    notification.add_tab("request", {
        "url": request.path_url,
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "params": dict(request.params),
    })
    notification.add_tab("environment", dict(request.environ))


# XXX bugsnag itself does not provide a paste filter factory
def bugsnag_filter(global_conf, **local_conf):
    if 'notify_release_stages' in local_conf:
        local_conf['notify_release_stages'] = local_conf[
            'notify_release_stages'].split(',')
    bugsnag.configure(**local_conf)

    def bugsnag_filter(app):
        return BugsnagMiddleware(app)
    return bugsnag_filter


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
