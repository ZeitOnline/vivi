from datetime import datetime
from unittest import mock
import urllib.error

import time_machine

import zeit.cms.checkout.interfaces
import zeit.cms.testing


class LockAPI(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        # API is available without authentication
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def test_status_200_for_unlocked(self):
        b = self.browser
        b.open('http://localhost/@@lock_status' '?uniqueId=http://xml.zeit.de/testcontent')
        self.assertEqual('200 Ok', b.headers['Status'])
        self.assert_json({'locked': False, 'owner': None, 'until': None})

    @time_machine.travel(datetime(2019, 1, 1), tick=False)
    def test_status_409_for_locked(self):
        zeit.cms.checkout.interfaces.ICheckoutManager(self.repository['testcontent']).checkout()
        b = self.browser
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('http://localhost/@@lock_status' '?uniqueId=http://xml.zeit.de/testcontent')
            self.assertEqual(409, info.exception.status)
        self.assert_json(
            {'locked': True, 'owner': 'zope.user', 'until': '2019-01-01T01:00:00+00:00'}
        )

    def test_resolves_uuid(self):
        b = self.browser
        # mock connector search() always returns
        # http://xml.zeit.de/online/2007/01/Somalia
        b.open('http://localhost/@@lock_status?uuid=dummy')
        self.assertEqual('200 Ok', b.headers['Status'])

    def test_resolves_interred_article_id(self):
        b = self.browser
        # mock connector search() always returns
        # http://xml.zeit.de/online/2007/01/Somalia
        b.open('http://localhost/@@lock_status?irid=dummy')
        self.assertEqual('200 Ok', b.headers['Status'])

    def test_status_404_for_nonexistent(self):
        b = self.browser
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('http://localhost/@@lock_status' '?uniqueId=http://xml.zeit.de/nonexistent')
            self.assertEqual(404, info.exception.status)

        with self.assertRaises(urllib.error.HTTPError) as info:
            with mock.patch('zeit.connector.mock.Connector.search') as search:
                search.return_value = None
                b.open('http://localhost/@@lock_status?uuid=dummy')
            self.assertEqual(404, info.exception.status)
