from urllib.parse import urlparse
import ast
import importlib.resources
import re

from ZODB.ActivityMonitor import ActivityMonitor
import grokcore.component as grok
import ZODB
import zodburi
import zope.app.appsetup.appsetup
import zope.component
import zope.component.hooks
import zope.configuration.config
import zope.configuration.xmlconfig
import zope.event
import zope.processlifetime

import zeit.cms.config


def bootstrap(settings):
    configure_product_config(settings)
    load_zcml(settings)
    db = create_zodb_database(settings['zodbconn.uri'])
    return db


def configure_product_config(settings):
    for key, value in settings.items():
        if not key.startswith('vivi_'):
            continue
        _, package, key = key.split('_')
        config = zeit.cms.config.package(package)
        config[key] = maybe_convert_egg_url(value)


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    u = urlparse(url)
    return 'file://%s' % (importlib.resources.files(u.netloc) / u.path[1:])


class ZCMLLoaded:
    """Event to run one-time setup code as part of ZCML execution,
    for setup that doesn't have a (single) "utility"-type result."""


def load_zcml(settings):
    feature = 'zcml.feature.'
    return _load_zcml(
        settings['site_zcml'],
        [
            x.replace(feature, '', 1)
            for x in settings
            if x.startswith(feature) and ast.literal_eval(settings[x])
        ],
    )


def _load_zcml(filename, features=(), package=None):
    # Modelled after zope.app.appsetup:config
    zope.component.hooks.setHooks()
    context = zope.configuration.config.ConfigurationMachine()
    setattr(zope.app.appsetup.appsetup, '__config_context', context)  # noqa
    for x in features:
        context.provideFeature(x)
    zope.configuration.xmlconfig.registerCommonDirectives(context)
    zope.configuration.xmlconfig.include(context, file=filename, package=package)
    context.execute_actions()
    zope.event.notify(ZCMLLoaded())
    return context


def create_zodb_database(uri):
    # Cobbled together from pyramid_zodbconn:includeme,
    # zope.app.appsetup:multi_database, zope.app.wsgi:config.
    dbmap = {}  # XXX We don't currently support multiple DBs.
    storage_factory, db_kw = zodburi.resolve_uri(uri)
    db = ZODB.DB(storage_factory(), databases=dbmap, **db_kw)
    db.setActivityMonitor(ActivityMonitor())
    zope.component.provideUtility(db, ZODB.interfaces.IDatabase)
    zope.event.notify(zope.processlifetime.DatabaseOpened(db))
    return db


class DelayedInitZODB:
    """A ZODB.DB shim that performs the actual initialization and storage
    creation only when open() is called, instead of directly in __init__().

    This supports using gunicorn.preload_app, thereby having to load ZCML only
    once, before forking the worker processes, which is a substantial
    performance benefit. The delayed init then creates the ZODB connection
    only afterwards (since it is not fork-safe).

    We can get away with not proxying any other methods, because all of Zope
    only ever uses IDatabase.open() and nothing else.
    """

    def __init__(self, uri):
        self.uri = uri

    def open(self, *args, **kw):
        db = zope.component.queryUtility(ZODB.interfaces.IDatabase)
        if db is None:
            db = create_zodb_database(self.uri)
        return db.open(*args, **kw)


@grok.subscribe(ZCMLLoaded)
def configure_dogpile_cache(event):
    import pyramid_dogpile_cache2

    regions = zeit.cms.config.required('zeit.cms', 'cache-regions')
    if not regions:
        return
    settings = {'dogpile_cache.regions': regions}
    for region in re.split(r'\s*,\s*', regions):
        settings[f'dogpile_cache.{region}.backend'] = 'dogpile.cache.memory'
        settings[f'dogpile_cache.{region}.expiration_time'] = zeit.cms.config.get(
            'zeit.cms', f'cache-expiration-{region}'
        )
    pyramid_dogpile_cache2.configure_dogpile_cache(settings)


try:
    import zope.principalregistry.principalregistry
except ImportError:  # UI-only dependency
    pass
else:

    @grok.subscribe(ZCMLLoaded)
    def set_passwords(event):
        config = zeit.cms.config.package('zeit.cms.principals')
        if not config:
            return
        registry = zope.principalregistry.principalregistry.principalRegistry
        for id, password in config.items():
            principal = registry.getPrincipal(id)
            principal._Principal__pw = password.encode('utf-8')
