from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.push.interfaces import IPushServices
import lxml.etree
import mock
import zeit.push.testing
import zeit.workflow.testing


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


class SendingNotifications(zeit.push.testing.TestCase):

    def setUp(self):
        super(SendingNotifications, self).setUp()
        self.notifier = mock.Mock()
        self.zca.patch_utility(
            self.notifier, zeit.push.interfaces.IPushNotifier, name='parse')

    def test_sends_title_and_translated_url(self):
        with checked_out(ICMSContent('http://xml.zeit.de/testcontent')) as co:
            co.title = 'mytitle'
        content = ICMSContent('http://xml.zeit.de/testcontent')

        zeit.push.workflow.send_push_notification(content, 'parse')
        self.notifier.send.assert_called_with(
            'mytitle', 'http://www.zeit.de/testcontent')

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_enabled_service_is_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        services = IPushServices(content)
        services.enabled = True
        services.parse = True
        self.publish(content)
        self.assertTrue(self.notifier.send.called)

    def test_disabled_service_is_not_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        services = IPushServices(content)
        services.enabled = True
        services.parse = False
        self.publish(content)
        self.assertFalse(self.notifier.send.called)
