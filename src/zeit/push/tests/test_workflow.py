from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.push.interfaces import IPushServices
import lxml.etree
import zeit.push.testing


class PushServiceProperties(zeit.push.testing.TestCase):

    def test_properties_can_be_set_while_checked_in(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        services = IPushServices(content)
        self.assertTrue(services.parse)
        services.parse = False
        self.assertFalse(services.parse)

    def test_properties_can_be_set_while_checked_out(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        with checked_out(content) as co:
            services = IPushServices(co)
            services.parse = False
        content = ICMSContent('http://xml.zeit.de/testcontent')
        services = IPushServices(content)
        self.assertFalse(services.parse)
        # These DAV properties are not serialized to XML.
        self.assertNotIn('parse', lxml.etree.tostring(
            content.xml, pretty_print=True))
