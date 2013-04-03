# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector which integrates into Zope CA and transaction machinery."""

import ZConfig
import ZODB.POSException
import logging
import os
import transaction
import transaction.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.component
import zope.event
import zope.interface
import zope.publisher.interfaces
import zope.security.interfaces
import zope.security.management


log = logging.getLogger(__name__)


class ZopeConnector(zeit.connector.connector.Connector):

    def create_connection(self, root):
        connection = super(self.__class__, self).create_connection(root)
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
        if not (zope.publisher.interfaces.http.IHTTPApplicationRequest
                .providedBy(request)):
            return None
        return request.getURL()

    def get_datamanager(self):
        conn = self.get_connection()
        return conn._connector_datamanager

    def lock(self, id, principal, until):
        locktoken = super(self.__class__, self).lock(id, principal, until)
        datamanager = self.get_datamanager()
        datamanager.add_cleanup(self.unlock, id, locktoken, False)
        return locktoken

    def unlock(self, id, locktoken=None, invalidate=True):
        locktoken = super(self.__class__, self).unlock(id, locktoken,
                                                      invalidate)
        self.get_datamanager().remove_cleanup(self.unlock, id, locktoken,
                                              False)
        return locktoken

    def move(self, old_id, new_id):
        super(ZopeConnector, self).move(old_id, new_id)
        # Only register clean up if move didn't fail:
        self.get_datamanager().add_cleanup(
            super(ZopeConnector, self).move, new_id, old_id)

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

    @property
    def locktokens(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.ILockInfoStorage)

    def _invalidate_cache(self, id):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(id))


def connectorFactory():
    """Factory for creating the connector with data from zope.conf."""
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    if config:
        root = config.get('document-store')
        if not root:
            raise ZConfig.ConfigurationError(
                "WebDAV server not configured properly.")
        search_root = config.get('document-store-search')
    else:
        root = os.environ.get('connector-url')
        search_root = os.environ.get('search-connector-url')

    if not root:
        raise ZConfig.ConfigurationError(
            "zope.conf has no product config for zeit.connector.")

    return ZopeConnector(dict(
        default=root,
        search=search_root))


class DataManager(object):
    """Takes care of the transaction process in Zope. """

    zope.interface.implements(transaction.interfaces.IDataManager)

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
            except:
                log.warning("Cleanup failed", exc_info=True)

        self.cleanup[:] = []


class ConnectorSavepoint(object):

    zope.interface.implements(transaction.interfaces.IDataManagerSavepoint)

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
