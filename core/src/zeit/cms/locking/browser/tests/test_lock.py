from datetime import datetime
import urllib.error

import time_machine

from zeit.cms.checkout.helper import checked_out
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.testing


class LockAPI(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        # API is available without authentication
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def test_status_200_for_unlocked(self):
        b = self.browser
        b.open('http://localhost/@@lock_status?uniqueId=http://xml.zeit.de/testcontent')
        self.assertEqual('200 Ok', b.headers['Status'])
        self.assert_json({'locked': False, 'owner': None, 'until': None})

    @time_machine.travel(datetime(2019, 1, 1), tick=False)
    def test_status_409_for_locked(self):
        zeit.cms.checkout.interfaces.ICheckoutManager(self.repository['testcontent']).checkout()
        b = self.browser
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('http://localhost/@@lock_status?uniqueId=http://xml.zeit.de/testcontent')
            self.assertEqual(409, info.exception.status)
        self.assert_json(
            {'locked': True, 'owner': 'zope.user', 'until': '2019-01-01T01:00:00+00:00'}
        )

    def test_resolves_uuid(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.repository['testcontent']).id
        b = self.browser
        b.open(f'http://localhost/@@lock_status?uuid={uuid}')
        self.assertEqual('200 Ok', b.headers['Status'])

    def test_resolves_interred_article_id(self):
        with checked_out(self.repository['testcontent']) as co:
            co.ir_article_id = 1234
        b = self.browser
        b.open('http://localhost/@@lock_status?irid=1234')
        self.assertEqual('200 Ok', b.headers['Status'])

    def test_status_404_for_nonexistent(self):
        b = self.browser
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('http://localhost/@@lock_status?uniqueId=http://xml.zeit.de/nonexistent')
            self.assertEqual(404, info.exception.status)

        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open(
                'http://localhost/@@lock_status?uuid={urn:uuid:00000000-0000-0000-0000-000000000000}'
            )
            self.assertEqual(404, info.exception.status)
