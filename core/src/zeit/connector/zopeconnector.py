import ZODB.POSException
import grokcore.component as grok
import logging
import transaction
import transaction.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zope.component
import zope.event
import zope.interface
import zope.publisher.interfaces
import zope.security.interfaces
import zope.security.management


log = logging.getLogger(__name__)


class ZopeConnector(zeit.connector.connector.Connector):
    """Connector which integrates into zope.component
    and transaction machinery."""

    def create_connection(self, root):
        connection = super().create_connection(root)
        dm = connection._connector_datamanager = DataManager(self)
        transaction.get().join(dm)
        url = self._get_calling_url()
        if url is not None:
            connection.additional_headers['Referer'] = url
        return connection

    def _get_calling_url(self):
        try:
            interaction = zope.security.management.getInteraction()
        except zope.security.interfaces.NoInteraction:
            return None
        if not interaction.participations:
            return None
        request = interaction.participations[0]
        return ICurrentURL(request, None)

    def get_datamanager(self):
        conn = self.get_connection()
        return conn._connector_datamanager

    def lock(self, id, principal, until):
        locktoken = super().lock(id, principal, until)
        datamanager = self.get_datamanager()
        datamanager.add_cleanup(self.unlock, id, locktoken, False)
        return locktoken

    def unlock(self, id, locktoken=None, invalidate=True):
        locktoken = super().unlock(id, locktoken, invalidate)
        self.get_datamanager().remove_cleanup(
            self.unlock, id, locktoken, False)
        return locktoken

    def move(self, old_id, new_id):
        super().move(old_id, new_id)
        # Only register clean up if move didn't fail:
        self.get_datamanager().add_cleanup(super().move, new_id, old_id)

    @property
    def body_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IResourceCache)

    @property
    def property_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IPropertyCache)

    @property
    def child_name_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IChildNameCache)

    def _invalidate_cache(self, id):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))


def connectorFactory():
    """Factory for creating the connector with data from zope.conf."""
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    return ZopeConnector({
        'default': config['document-store'],
        'search': config['document-store-search']})


@zope.interface.implementer(transaction.interfaces.IDataManager)
class DataManager(object):
    """Takes care of the transaction process in Zope. """

    def __init__(self, connector):
        self.connector = connector
        self.cleanup = []

    def abort(self, trans):
        self._cleanup()
        self.connector.disconnect()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.connector.disconnect()

    def tpc_abort(self, trans):
        self._cleanup()
        self.connector.disconnect()

    def sortKey(self):
        return str(id(self))

    def savepoint(self):
        # This would be a point to flush pending commands.
        return ConnectorSavepoint()

    def add_cleanup(self, method, *args, **kwargs):
        self.cleanup.append((method, args, kwargs))

    def remove_cleanup(self, method, *args, **kwargs):
        try:
            self.cleanup.remove((method, args, kwargs))
        except ValueError:
            pass

    def _cleanup(self):
        for method, args, kwargs in self.cleanup:
            log.info("Abort cleanup: %s(%s, %s)" % (method, args, kwargs))
            try:
                method(*args, **kwargs)
            except ZODB.POSException.ConflictError:
                raise
            except Exception:
                log.warning("Cleanup failed", exc_info=True)

        self.cleanup[:] = []


@zope.interface.implementer(transaction.interfaces.IDataManagerSavepoint)
class ConnectorSavepoint(object):

    def rollback(self):
        raise Exception("Can't roll back connector savepoints.")


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_cache(event):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    try:
        connector.invalidate_cache(event.id)
    except ValueError:
        # The connector isn't responsible for the id, or the id is just plain
        # invalid. There is nothing to invalidate then anyway.
        pass


class ICurrentURL(zope.interface.Interface):
    pass


@grok.adapter(zope.publisher.interfaces.http.IHTTPApplicationRequest)
@grok.implementer(ICurrentURL)
def http_current_url(request):
    return request.getURL()


@grok.adapter(zope.interface.Interface)
@grok.implementer(ICurrentURL)
def default_current_url(request):
    return getattr(request, '_zeit_connector_referrer', None)
