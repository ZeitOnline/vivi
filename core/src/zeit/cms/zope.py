from ZODB.ActivityMonitor import ActivityMonitor
import ZODB
import zodburi
import zope.component
import zope.event
import zope.processlifetime


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
