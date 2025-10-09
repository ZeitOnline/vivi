from unittest import mock

import zope.component

import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.webtest


class XMLRPCTest(zeit.cms.testing.BrowserTestCase):
    layer = zeit.cms.testing.WSGI_LAYER

    def setUp(self):
        super().setUp()
        server = zeit.cms.webtest.ServerProxy(
            'http://notify:notifypw@localhost/', self.layer['wsgi_app']
        )
        self.notify = getattr(server, '@@notify')

    def test_notify_cms(self):
        notify = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            notify, (zeit.cms.content.interfaces.IContentModifiedEvent,)
        )
        self.notify('http://xml.zeit.de/testcontent')
        self.assertTrue(notify.called)
        self.assertEqual('http://xml.zeit.de/testcontent', notify.call_args.args[0].object.uniqueId)
