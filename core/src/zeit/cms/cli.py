from configparser import ConfigParser
import argparse
import logging
import os
import os.path
import signal
import sys
import time

from opentelemetry.trace import SpanKind
import opentelemetry.context
import transaction
import transaction.interfaces
import zope.component
import zope.component.hooks

import zeit.cms.logging
import zeit.cms.tracing


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
    paste.optionxform = str  # Don't lower-case keys
    paste.read(paste_ini)
    return dict(paste.items('application:main'))


SETTINGS = {}


def configure(settings):
    global SETTINGS
    if SETTINGS:
        log.warning('zeit.cms.cli.configure() called twice')

    # Shells support only [a-z-A-Z0-9_] in environment variable names,
    # but pyramid and friends needs `.`, and vivi product config needs `-`.
    # See <https://stackoverflow.com/a/36992531>
    updates = []
    for key, value in settings.items():
        if not ('__dot__' in key or '__dash__' in key):
            continue
        new = key.replace('__dot__', '.').replace('__dash__', '-')
        updates.append((key, new, value))
    for old, new, value in updates:
        settings[new] = value
        del settings[old]

    # Kludge for local environment that uses paste.ini files
    pgservicefile = settings.get('PGSERVICEFILE')
    if pgservicefile:
        os.environ['PGSERVICEFILE'] = pgservicefile

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
            # copy&paste to adjust exception handling in `once` mode.
            old_site = zope.component.hooks.getSite()
            zope.component.hooks.setSite(self.app)

            self._is_running = True

            while self._is_running:
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
                        'controller': 'cli',
                        'route': self.worker.__name__,
                        # 'action':
                    },
                    context,
                )
                context = opentelemetry.context.attach(context)

                ticks = None
                self.begin()
                try:
                    tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
                    with tracer.start_as_current_span(
                        'cli %s' % self.worker.__name__, kind=SpanKind.SERVER
                    ):
                        ticks = self.worker()
                except (KeyboardInterrupt, SystemExit):
                    self.abort()
                    break
                except Exception:
                    self.abort()
                    if self.once:
                        raise
                    else:
                        log.error('Error in worker', exc_info=True)
                else:
                    try:
                        self.commit()
                    except transaction.interfaces.TransientError:
                        self.abort()
                        if self.once:
                            raise
                        else:
                            # Ignore silently, the next run will retry.
                            log.warning('Conflict error', exc_info=True)
                finally:
                    if context is not None:
                        opentelemetry.context.detach(context)

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
    parser.add_argument('--user', '-u', help='username, e.g. email', default='system.teamcontent')
    options, left = parser.parse_known_args()
    sys.argv = sys.argv[:1] + left
    if not options.user:
        parser.print_help()
        raise SystemExit(1)
    return options.user


@runner(principal=principal_from_args)
def provide_interface():
    import zope.container.contained
    import zope.dottedname.resolve
    import zope.interface
    import zope.proxy

    from zeit.cms.type import _provides_dav_property
    from zeit.connector.resource import PropertyKey
    import zeit.cms.content.interfaces
    import zeit.cms.interfaces
    import zeit.connector.interfaces

    parser = argparse.ArgumentParser(description='Provide an interface to a content object')
    parser.add_argument('uniqueId')
    parser.add_argument('interface')
    options = parser.parse_args()

    content = zeit.cms.interfaces.ICMSContent(options.uniqueId)
    # Unwrap so we don't get confused by interface-declarations of any proxy.
    content = zope.proxy.removeAllProxies(content)
    # Dear Zope, why is ContainedProxy not a zope.proxy?
    content = zope.container.contained.getProxiedObject(content)
    iface = zope.dottedname.resolve.resolve(options.interface)
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

    try:
        # We don't want to store this in the DAV property, since it always comes
        # from the Repository when needed.
        zope.interface.noLongerProvides(content, zeit.cms.repository.interfaces.IRepositoryContent)
    except Exception:
        pass

    zope.interface.alsoProvides(content, iface)
    # work around security, reimplement the parts of DAVProperty.__set__ and
    # LiveProperties.__setitem__ that actually set the value
    read_properties = zeit.cms.interfaces.IWebDAVReadProperties(content)
    field = _provides_dav_property.field.bind(content)
    key = PropertyKey(_provides_dav_property.name, _provides_dav_property.namespace)
    converter = zope.component.getMultiAdapter(
        (field, read_properties, key), zeit.cms.content.interfaces.IDAVPropertyConverter
    )
    dav_value = converter.toProperty(content.__provides__)
    connector.changeProperties(content.uniqueId, {key: dav_value})

    # Committing is not technically necessary (neither DAV nor the connector care),
    # but it's good form, and if it's there, nobody will be confused as to why it's
    # missing and whether it would have been needed.
    transaction.commit()
