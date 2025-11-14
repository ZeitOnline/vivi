from unittest import mock

import zope.component

import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.webtest
import zeit.connector.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.cms.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER

    def setUp(self):
        super().setUp()
        server = zeit.cms.webtest.ServerProxy(
            'http://notify:notifypw@localhost/', self.layer['wsgi_app']
        )
        self.content_modified_request = getattr(server, '@@content_modified')

        self.resource_invalidate = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            self.resource_invalidate, (zeit.connector.interfaces.ResourceInvalidatedEvent,)
        )
        self.content_modified = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            self.content_modified, (zeit.cms.content.interfaces.IContentModifiedEvent,)
        )
        self.update_index = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            self.update_index, (zeit.cms.checkout.interfaces.IContentIndexEvent,)
        )

    def tearDown(self):
        zope.component.getGlobalSiteManager().unregisterHandler(
            self.resource_invalidate, (zeit.connector.interfaces.ResourceInvalidatedEvent,)
        )
        zope.component.getGlobalSiteManager().unregisterHandler(
            self.content_modified, (zeit.cms.content.interfaces.IContentModifiedEvent,)
        )
        zope.component.getGlobalSiteManager().unregisterHandler(
            self.update_index, (zeit.cms.checkout.interfaces.IContentIndexEvent,)
        )
        super().tearDown()
