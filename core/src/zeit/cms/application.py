import fanstatic
import os
import pkg_resources
import werkzeug.debug
import zope.app.wsgi.paste


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
        app = zope.app.wsgi.paste.ZopeApplication(
            global_conf, local_conf['zope_conf'], handle_errors=not debug)
        if debug:
            self.pipeline.insert(
                0, (werkzeug.debug.DebuggedApplication, 'factory', '', {
                    'evalex': True}))
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
