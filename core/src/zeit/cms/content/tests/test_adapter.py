from unittest import mock
import lxml.etree
import zeit.cms.checkout.interfaces
import zeit.cms.testing


class XMLSafeguardTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_tostring_yields_invalid_xml_should_raise(self):
        co = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['testcontent']
        ).checkout()
        manager = zeit.cms.checkout.interfaces.ICheckinManager(co)
        with mock.patch('lxml.etree.tostring') as tostring:
            tostring.return_value = 'invalid'
            with self.assertRaises(lxml.etree.XMLSyntaxError):
                manager.checkin()
