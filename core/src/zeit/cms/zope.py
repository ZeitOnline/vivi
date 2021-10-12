from ZODB.ActivityMonitor import ActivityMonitor
import ZODB
import zodburi
import zope.component
import zope.component.hooks
import zope.configuration.config
import zope.configuration.xmlconfig
import zope.event
import zope.processlifetime


def load_zcml(filename):
    # Modelled after zope.app.appsetup:config
    zope.component.hooks.setHooks()
    context = zope.configuration.config.ConfigurationMachine()
    zope.configuration.xmlconfig.registerCommonDirectives(context)
    zope.configuration.xmlconfig.include(context, file=filename)
    context.execute_actions()
    return context


def zodb_connection(uri):
    # Cobbled together from pyramid_zodbconn:includeme,
    # zope.app.appsetup:multi_database, zope.app.wsgi:config.
    dbmap = {}  # XXX We don't currently support multiple DBs.
    storage_factory, db_kw = zodburi.resolve_uri(uri)
    db = ZODB.DB(storage_factory(), databases=dbmap, **db_kw)
    db.setActivityMonitor(ActivityMonitor())
    zope.component.provideUtility(db, ZODB.interfaces.IDatabase)
    zope.event.notify(zope.processlifetime.DatabaseOpened(db))
    return db
