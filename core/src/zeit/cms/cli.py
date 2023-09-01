from configparser import ConfigParser
import logging
import os
import os.path
import signal
import sys
import time
import zeit.cms.logging


log = logging.getLogger(__name__)


def zope_shell():
    import zeit.cms.zope
    import zope.component.hooks
    settings = parse_paste_ini()
    db = zeit.cms.zope.bootstrap(settings)
    # Adapted from zc.zope3recipes.debugzope.debug()
    globs = {
        '__name__': '__main__',
        # zope.app.publication.ZopePublication.root_name
        'root': db.open().root()['Application'],
        'zeit': sys.modules['zeit'],
        'zope': sys.modules['zope'],
        'transaction': sys.modules['transaction'],
    }
    if len(sys.argv) > 1:
        sys.argv[:] = sys.argv[1:]
        globs['__file__'] = sys.argv[0]
        exec(compile(  # noqa
            open(sys.argv[0], "rb").read(), sys.argv[0], 'exec'), globs)
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
    settings = os.environ.copy()
    if len(sys.argv) >= 2 and sys.argv[1].endswith('.ini'):
        settings.update(_parse_paste_ini(sys.argv.pop(1)))
    configure(settings)
    return settings


def _parse_paste_ini(paste_ini):
    paste = ConfigParser()
    paste.read(paste_ini)
    return dict(paste.items('application:main'))


SETTINGS = {}


def configure(settings):
    global SETTINGS
    if SETTINGS:
        log.warning('zeit.cms.cli.configure() called twice')
    SETTINGS = settings
    _configure_logging(settings)


def _configure_logging(settings):
    config = {
        key.replace('logging.', '', 1): value for key, value in
        settings.items() if key.startswith('logging.')}
    if config:
        zeit.cms.logging.configure(config)


try:
    import gocept.runner
    from gocept.runner import from_config  # noqa API
except ImportError:
    # Provide fake decorator so zeit.web can avoid importing the zope machinery
    def runner(*args, **kw):
        return lambda x: x

    def from_config(*args, **kw):
        return None
else:
    class runner(gocept.runner.appmain):

        def __init__(self, ticks=1, principal=None, once=True):
            super().__init__(ticks=ticks, principal=principal)
            self.once = once

        def __call__(self, worker_method):
            # copy&paste to adjust configuration handling.
            def run():
                import zeit.cms.zope
                settings = parse_paste_ini()
                try:
                    db = zeit.cms.zope.bootstrap(settings)
                    root = db.open().root()
                    # zope.app.publication.ZopePublication.root_name
                    app = root['Application']
                    mloop = gocept.runner.runner.MainLoop(
                        app, self.ticks, worker_method,
                        principal=self.get_principal(), once=self.once)
                    signal.signal(signal.SIGHUP, mloop.stopMainLoop)
                    signal.signal(signal.SIGTERM, mloop.stopMainLoop)
                    mloop()
                finally:
                    db.close()
            return run


def wait_for_commit(func):
    from ZODB.POSException import ConflictError
    import transaction
    while True:
        func()
        try:
            transaction.commit()
            return
        except ConflictError:
            log.warning('ConflictError, retrying')
            transaction.abort()
            time.sleep(0.5)
