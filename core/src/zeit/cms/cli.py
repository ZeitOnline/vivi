from configparser import ConfigParser
import argparse
import logging
import os
import os.path
import signal
import sys
import time

import transaction
import ZODB.POSException
import zope.component.hooks

import zeit.cms.logging


log = logging.getLogger(__name__)


def zope_shell():
    import zeit.cms.zope

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
    from gocept.runner import from_config  # noqa API
    import gocept.runner
except ImportError:
    # Provide fake decorator so zeit.web can avoid importing the zope machinery
    def runner(*args, **kw):
        return lambda x: x

    def from_config(*args, **kw):
        return None
else:

    class MainLoop(gocept.runner.runner.MainLoop):
        def __call__(self):
            old_site = zope.component.hooks.getSite()
            zope.component.hooks.setSite(self.app)

            self._is_running = True

            while self._is_running:
                ticks = None
                self.begin()
                try:
                    ticks = self.worker()
                except (KeyboardInterrupt, SystemExit):
                    self.abort()
                    break
                except Exception as e:
                    log.error('Error in worker: %s', repr(e), exc_info=True)
                    self.abort()
                else:
                    try:
                        self.commit()
                    except ZODB.POSException.ConflictError:
                        # Ignore silently, the next run will be a retry anyway.
                        log.warning('Conflict error', exc_info=True)
                        self.abort()

                if self.once or ticks is gocept.runner.Exit:
                    self._is_running = False
                else:
                    if ticks is None:
                        ticks = self.ticks
                    log.debug('Sleeping %s seconds' % ticks)
                    time.sleep(ticks)

            zope.component.hooks.setSite(old_site)

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
                    mloop = MainLoop(
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


def commit_with_retry(*, attempts=3, wait=0.5):
    # We (ab)use `for` as a repeatable `with`. Simplified version of e.g.
    # https://stamina.hynek.me/en/stable/tutorial.html#arbitrary-code-blocks
    # as we don't catch exceptions raised inside the block here.
    for i in range(1, attempts + 1):
        yield i
        try:
            transaction.commit()
        except transaction.interfaces.TransientError:
            log.info('ConflictError, retry attempt %s/%s', i, attempts)
            transaction.abort()
            if i == attempts:
                raise
            time.sleep(wait)
        else:
            break


def login(username):
    import z3c.celery.celery

    z3c.celery.celery.login_principal(
        z3c.celery.celery.get_principal(username), 'console.PUBLISH_TASK'
    )


def principal_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', '-u', help='username, e.g. email')
    options, left = parser.parse_known_args()
    sys.argv = sys.argv[:1] + left
    if not options.user:
        parser.print_help()
        raise SystemExit(1)
    return options.user
