from ZODB.ActivityMonitor import ActivityMonitor
from urllib.parse import urlparse
import ZODB
import ast
import grokcore.component as grok
import pkg_resources
import re
import zodburi
import zope.app.appsetup.appsetup
import zope.app.appsetup.product
import zope.component
import zope.component.hooks
import zope.configuration.config
import zope.configuration.xmlconfig
import zope.event
import zope.processlifetime


def bootstrap(settings):
    configure_product_config(settings)
    load_zcml(settings)
    db = create_zodb_database(settings['zodbconn.uri'])
    return db


def configure_product_config(settings):
    for key, value in settings.items():
        if not key.startswith('vivi_'):
            continue

        ignored, package, setting = key.split('_')
        if zope.app.appsetup.product.getProductConfiguration(package) is None:
            zope.app.appsetup.product.setProductConfiguration(package, {})
        config = zope.app.appsetup.product.getProductConfiguration(package)
        value = maybe_convert_egg_url(value)
        config[setting] = value


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    u = urlparse(url)
    return 'file://' + pkg_resources.resource_filename(u.netloc, u.path[1:])


def load_zcml(settings):
    feature = 'zcml.feature.'
    return _load_zcml(
        settings['site_zcml'],
        [x.replace(feature, '', 1) for x in settings
         if x.startswith(feature) and ast.literal_eval(settings[x])])


def _load_zcml(filename, features=()):
    # Modelled after zope.app.appsetup:config
    zope.component.hooks.setHooks()
    context = zope.configuration.config.ConfigurationMachine()
    setattr(zope.app.appsetup.appsetup, '__config_context', context)
    for x in features:
        context.provideFeature(x)
    zope.configuration.xmlconfig.registerCommonDirectives(context)
    zope.configuration.xmlconfig.include(context, file=filename)
    context.execute_actions()
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


@grok.subscribe(zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
def configure_dogpile_cache(event):
    import pyramid_dogpile_cache2
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    settings = {
        'dogpile_cache.regions': config['cache-regions']
    }
    for region in re.split(r'\s*,\s*', config['cache-regions']):
        settings['dogpile_cache.%s.backend' % region] = 'dogpile.cache.memory'
        settings['dogpile_cache.%s.expiration_time' % region] = config[
            'cache-expiration-%s' % region]
    pyramid_dogpile_cache2.configure_dogpile_cache(settings)


try:
    import zope.principalregistry.principalregistry
except ImportError:  # UI-only dependency
    pass
else:
    @grok.subscribe(zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
    def set_passwords(event):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms.principals')
        if not config:
            return
        registry = zope.principalregistry.principalregistry.principalRegistry
        for id, password in config.items():
            principal = registry.getPrincipal(id)
            principal._Principal__pw = password.encode('utf-8')
