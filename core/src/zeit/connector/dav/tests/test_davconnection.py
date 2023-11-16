from io import BytesIO
import unittest
import zeit.connector.dav.davbase
import zeit.connector.dav.davconnection


class TestPropfind(unittest.TestCase):
    response = ''

    def setUp(self):
        self.count = 0
        self.conn = zeit.connector.dav.davconnection.DAVConnection('localhost')
        self._orig_propfind = zeit.connector.dav.davbase.DAVConnection.propfind
        zeit.connector.dav.davbase.DAVConnection.propfind = self.propfind

    def tearDown(self):
        zeit.connector.dav.davbase.DAVConnection.propfind = self._orig_propfind

    def propfind(self, *args, **kwargs):
        self.count += 1
        result = BytesIO(self.response.encode('utf-8'))
        result.status = 207
        result.reason = 'Multi Status'
        result.getheader = lambda x, y=None: y
        return result

    def test_propfind_retries_incomplete_results(self):
        self.verifyRaisesAfter('<a><b></b>', 3)

    def test_xml_errors_raise(self):
        self.verifyRaisesAfter('garbage', 1)
        self.verifyRaisesAfter('<a>&</a>', 1)

    def test_valid_returns_result(self):
        self.response = '<a><b/></a>'
        result = self.conn.propfind('/')
        self.assertEqual(207, result.status)

    def verifyRaisesAfter(self, xml, count):
        self.response = xml
        self.assertRaises(zeit.connector.dav.interfaces.DavXmlParseError, self.conn.propfind, '/')
        self.assertEqual(count, self.count)
        self.count = 0
