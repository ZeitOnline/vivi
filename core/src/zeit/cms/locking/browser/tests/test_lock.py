from datetime import datetime
import mock
import pytz
import time
import urllib2
import zeit.cms.checkout.interfaces
import zeit.cms.testing
import zope.app.locking.lockinfo


class TimeFreezeLockInfo(zope.app.locking.lockinfo.LockInfo):

    def __init__(self, *args, **kw):
        super(TimeFreezeLockInfo, self).__init__(*args, **kw)
        self.created = time.mktime(
            datetime(2019, 4, 15, 18, 20, tzinfo=pytz.UTC).timetuple())


class LockAPI(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def setUp(self):
        super(LockAPI, self).setUp()
        # API is available without authentication
        self.browser = zeit.cms.testing.Browser()

    def test_status_200_for_unlocked(self):
        b = self.browser
        b.open('http://localhost/@@lock_status'
               '?uniqueId=http://xml.zeit.de/testcontent')
        self.assertEqual('200 Ok', b.headers['Status'])
        self.assert_json({'locked': False, 'owner': None, 'until': None})

    def test_status_409_for_locked(self):
        with mock.patch('zope.app.locking.adapter.LockInfo',
                        new=TimeFreezeLockInfo):
            zeit.cms.checkout.interfaces.ICheckoutManager(
                self.repository['testcontent']).checkout()
        b = self.browser
        with self.assertRaises(urllib2.HTTPError) as info:
            b.open('http://localhost/@@lock_status'
                   '?uniqueId=http://xml.zeit.de/testcontent')
            self.assertEqual(409, info.exception.status)
        self.assert_json({'locked': True, 'owner': 'zope.user',
                          'until': '2019-04-15T18:20:00+00:00'})

    def test_resolves_uuid(self):
        b = self.browser
        # mock connector search() always returns
        # http://xml.zeit.de/online/2007/01/Somalia
        b.open('http://localhost/@@lock_status?uuid=dummy')
        self.assertEqual('200 Ok', b.headers['Status'])

    def test_status_404_for_nonexistent(self):
        b = self.browser
        with self.assertRaises(urllib2.HTTPError) as info:
            b.open('http://localhost/@@lock_status'
                   '?uniqueId=http://xml.zeit.de/nonexistent')
            self.assertEqual(404, info.exception.status)

        with self.assertRaises(urllib2.HTTPError) as info:
            with mock.patch('zeit.connector.mock.Connector.search') as search:
                search.return_value = None
                b.open('http://localhost/@@lock_status?uuid=dummy')
            self.assertEqual(404, info.exception.status)
