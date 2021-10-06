from configparser import ConfigParser
import logging.config
import os
import os.path
import signal
import sys


def zope_shell():
    import zope.app.wsgi
    import zope.component.hooks
    # XXX How to get to zope.conf is the only-application specific part.
    zope_conf = parse_paste_ini()
    db = zope.app.wsgi.config(zope_conf)
    # Adapted from zc.zope3recipes.debugzope.debug()
    globs = {
        '__name__': '__main__',
        # Not really worth using zope.app.publication.ZopePublication.root_name
        'root': db.open().root()['Application'],
        'zeit': sys.modules['zeit'],
        'zope': sys.modules['zope'],
        'transaction': sys.modules['transaction'],
    }
    if len(sys.argv) > 1:
        sys.argv[:] = sys.argv[1:]
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


def parse_paste_ini():
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s paste.ini\n' % sys.argv[0])
        sys.exit(1)
    paste_ini = sys.argv.pop(1)
    logging.config.fileConfig(
        paste_ini, {'__file__': paste_ini, 'here': os.path.abspath(
            os.path.dirname(paste_ini))})
    paste = ConfigParser()
    paste.read(paste_ini)
    settings = os.environ.copy()
    for key, value in paste.items('application:main'):
        settings[key] = value
    configure(settings)
    return settings['zope_conf']


def configure(settings):
    _configure_celery(settings)


def _configure_celery(settings):
    if 'CELERY_CONFIG_FILE' not in os.environ:
        # See z3c.celery.loader. Depending on our deployment setup it may be
        # more sensible to centralize this in paste.ini than to use env vars.
        os.environ['CELERY_CONFIG_FILE'] = settings.get('celery_conf')


try:
    import gocept.runner
except ImportError:
    # Provide fake decorator so zeit.web can avoid importing the zope machinery
    def runner(*args, **kw):
        return lambda x: x
else:
    class runner(gocept.runner.appmain):

        def __init__(self, ticks=1, principal=None, once=True):
            super().__init__(ticks=ticks, principal=principal)
            self.once = once

        def __call__(self, worker_method):
            # copy&paste to retrieve config file from argv instead of buildout
            def run():
                zope_conf = parse_paste_ini()
                with gocept.runner.runner.init(None, zope_conf) as app:
                    mloop = gocept.runner.runner.MainLoop(
                        app, self.ticks, worker_method,
                        principal=self.get_principal(), once=self.once)
                    signal.signal(signal.SIGHUP, mloop.stopMainLoop)
                    signal.signal(signal.SIGTERM, mloop.stopMainLoop)
                    mloop()
            return run
