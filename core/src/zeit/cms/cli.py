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
    zope.component.hooks.setSite(globs['root'])
    if len(sys.argv) > 1:
        sys.argv[:] = sys.argv[1:]
        globs['__file__'] = sys.argv[0]
        exec(
            compile(  # noqa
                open(sys.argv[0], 'rb').read(), sys.argv[0], 'exec'
            ),
            globs,
        )
        sys.exit()
    else:
        import code

        # Modeled after pyramid.scripts.pshell
        code.interact(
            local=globs,
            banner="""\
Python %s on %s
Type "help" for more information.

Environment:
  root         ZODB application root folder (already set as ZCA site)
Modules that were pre-imported for convenience: zope, zeit, transaction
"""
            % (sys.version, sys.platform),
        )


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
        key.replace('logging.', '', 1): value
        for key, value in settings.items()
        if key.startswith('logging.')
    }
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
                        app,
                        self.ticks,
                        worker_method,
                        principal=self.get_principal(),
                        once=self.once,
                    )
                    signal.signal(signal.SIGHUP, mloop.stopMainLoop)
                    signal.signal(signal.SIGTERM, mloop.stopMainLoop)
                    mloop()
                finally:
                    db.close()

            return run


def wait_for_commit(content, max_attempts):
    import transaction

    attempts = 0
    try:
        transaction.commit()
    except Exception:
        transaction.abort()
        time.sleep(0.5)
        while attempts <= max_attempts:
            # If commit could not be performed, we try again with explicit
            # cache invalidation. Otherwise there is nothing left to commit
            # after the first `transaction.abort()`.
            zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(content.uniqueId))
            try:
                transaction.commit()
                break
            except Exception:
                transaction.abort()
                time.sleep(0.5)
                attempts += 1
    if attempts > max_attempts:
        return False
    return True


def login(username):
    import z3c.celery.celery

    z3c.celery.celery.login_principal(
        z3c.celery.celery.get_principal(username), 'console.PUBLISH_TASK'
    )
