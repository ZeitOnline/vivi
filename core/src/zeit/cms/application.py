from ConfigParser import ConfigParser
import ZConfig
import ast
import bugsnag
import bugsnag.wsgi
import bugsnag.wsgi.middleware
import fanstatic
import fnmatch
import grokcore.component as grok
import grokcore.component.zcml
import logging.config
import martian
import os
import pkg_resources
import pyramid_dogpile_cache2
import re
import sys
import webob
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.wsgi
import zope.app.wsgi.paste
import zope.component.hooks


FANSTATIC_PATH = fanstatic.DEFAULT_SIGNATURE
FANSTATIC_DEBUG = os.environ.get('FANSTATIC_DEBUG', False)
FANSTATIC_VERSIONING = os.environ.get('FANSTATIC_VERSIONING', True)
BUNDLE = not FANSTATIC_DEBUG
MINIFIED = False  # XXX


class Application(object):

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


class ClearFanstaticOnError(object):
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


CONFIG_CACHE = pyramid_dogpile_cache2.get_region('config')
FEATURE_CACHE = pyramid_dogpile_cache2.get_region('feature')


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
        execfile(sys.argv[0], globs)
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
    if config.get('cache-redis-url', '').strip():
        import zeit.connector.cache
        settings['dogpile_cache.regions'] += ', dav'
        pyramid_dogpile_cache2.CACHE_REGIONS[
            'dav'] = zeit.connector.cache.DAV_CACHE

        settings.update({
            'dogpile_cache.dav.backend': 'dogpile.cache.redis',
            'dogpile_cache.dav.arguments.url': config['cache-redis-url'],
        })
    for region in re.split(r'\s*,\s*', config['cache-regions']):
        settings['dogpile_cache.%s.backend' % region] = 'dogpile.cache.memory'
        settings['dogpile_cache.%s.expiration_time' % region] = config[
            'cache-expiration-%s' % region]
    pyramid_dogpile_cache2.configure_dogpile_cache(settings)


class BugsnagMiddleware(object):

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


try:
    import fluent.handler
except ImportError:
    pass  # soft dependency
else:
    class FluentRecordFormatter(fluent.handler.FluentRecordFormatter):
        """Work around the fact that `logging.fileConfig` (which most clients
        use) is not based on `logging.dictConfig` and thus is less expressive,
        especially concerning Formatter instantiation: it only supports a
        (string) `format=` parameter, and nothing else. Since
        FluentRecordFormatter needs a dict, we call literal_eval so it works.
        """

        def __init__(self, fmt=None, datefmt=None, **kw):
            if isinstance(fmt, basestring) and fmt.strip().startswith('{'):
                fmt = ast.literal_eval(fmt)
            super(FluentRecordFormatter, self).__init__(fmt, **kw)


# Backport ZConfig-2.x behaviour of assuming UTF-8, not ASCII.
# (Actually the old behaviour probably was to rely on the py2 str laxness, but
# all we really want is utf-8, so that's alright.)
def maybe_encode(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return value

ZConfig.datatypes.stock_datatypes["string"] = maybe_encode
