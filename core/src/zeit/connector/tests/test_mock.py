from datetime import datetime, timedelta
from unittest import mock
import io
import logging

from pytz import UTC
import transaction

from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.connector.search import SearchVar as SV
import zeit.connector.testing


class MockConnectorTest(zeit.connector.testing.MockTest):
    def setUp(self):
        super().setUp()
        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.handler)

    def tearDown(self):
        logging.root.removeHandler(self.handler)
        super().tearDown()

    def test_reset_forgets_writes(self):
        self.connector.add(self.get_resource('foo'))
        self.assertIn('http://xml.zeit.de/testing/foo', self.connector)
        self.connector._reset()
        self.assertNotIn('http://xml.zeit.de/testing/foo', self.connector)

    def test_search_is_mocked_and_logs_query(self):
        author = SV('author', 'http://namespaces.zeit.de/CMS/document')
        volume = SV('volume', 'http://namespaces.zeit.de/CMS/document')
        ressort = SV('ressort', 'http://namespaces.zeit.de/CMS/document')
        result = list(
            self.connector.search([author, volume, ressort], (volume == '07') & (author == 'pm'))
        )
        self.assertEqual(
            [
                ('http://xml.zeit.de/online/2007/01/Somalia', 'pm', '07', None),
                ('http://xml.zeit.de/online/2007/01/Saarland', 'pm', '07', None),
                ('http://xml.zeit.de/2006/52/Stimmts', 'pm', '07', None),
            ],
            result,
        )
        self.assertEllipsis(
            """\
Searching: (:and
  (:eq "http://namespaces.zeit.de/CMS/document" "volume" "07")
  (:eq "http://namespaces.zeit.de/CMS/document" "author" "pm"))...""",
            self.log.getvalue(),
        )

    def test_foreign_lock_does_not_break_if_utility_is_missing(self):
        from zeit.connector.lock import lock_is_foreign

        with mock.patch('zeit.connector.lock.HAVE_AUTH', new=False):
            self.assertTrue(lock_is_foreign('zope.user'))

    def test_switch_of_locking(self):
        """Locking can be switched of for zeit.web tests, therefore a resource locked by another
        user can be altered.
        """
        self.connector.ignore_locking = True
        res = self.add_resource('foo')
        self.connector.lock(res.id, 'external', datetime.now(UTC) + timedelta(hours=2))
        transaction.commit()
        res = self.get_resource('foo')
        self.connector['http://xml.zeit.de/testing/foo'] = res


class CollectionPropertyTest(zeit.connector.testing.MockTest):
    def test_channels(self):
        from zeit.cms.content.sources import FEATURE_TOGGLES

        dav_format = 'channel1;channel2 sub1'
        regular_format = [['channel1', None], ['channel2', 'sub1']]
        FEATURE_TOGGLES.set('write_metadata_columns', True)
        res = self.add_resource(
            'foo', properties={('channels', DOCUMENT_SCHEMA_NS): regular_format}
        )
        self.assertEqual(res.properties[('channels', DOCUMENT_SCHEMA_NS)], dav_format)
        FEATURE_TOGGLES.set('read_metadata_columns', True)
        res = self.connector[res.id]
        self.assertEqual(res.properties[('channels', DOCUMENT_SCHEMA_NS)], regular_format)
