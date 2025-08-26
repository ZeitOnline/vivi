import zope.component
import zope.interface

import zeit.connector.interfaces
import zeit.connector.mock

from .layer import Layer


class ResetMocks:
    """ZCA event for pluggable reset handlers that run on testTearDown."""


class MockResetLayer(Layer):
    event = (zope.interface.providedBy(ResetMocks()),)

    def testTearDown(self):
        registry = zope.component.getSiteManager().adapters
        # Like zope.event.notify(), but expects handlers to take no parameters
        # (instead of the event object)
        for func in registry.subscriptions(self.event, None):
            func()


MOCK_RESET_LAYER = MockResetLayer()


def reset_connector():
    connector = zope.component.queryUtility(zeit.connector.interfaces.IConnector)
    if isinstance(connector, zeit.connector.mock.Connector):
        connector._reset()
