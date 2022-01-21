from zeit.connector.search import SearchVar as SV
import io
import logging
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
        result = list(self.connector.search(
            [author, volume, ressort],
            (volume == '07') & (author == 'pm')))
        self.assertEqual(
            [('http://xml.zeit.de/online/2007/01/Somalia', 'pm', '07', None),
             ('http://xml.zeit.de/online/2007/01/Saarland', 'pm', '07', None),
             ('http://xml.zeit.de/2006/52/Stimmts', 'pm', '07', None)],
            result)
        self.assertEllipsis("""\
Searching: (:and
  (:eq "http://namespaces.zeit.de/CMS/document" "volume" "07")
  (:eq "http://namespaces.zeit.de/CMS/document" "author" "pm"))...""",
                            self.log.getvalue())
