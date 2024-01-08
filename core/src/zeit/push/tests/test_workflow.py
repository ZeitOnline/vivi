from unittest import mock

import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish
from zeit.push.interfaces import IPushMessages
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.push.testing


class PushServiceProperties(zeit.push.testing.TestCase):
    def test_properties_can_be_set_while_checked_in(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.message_config = [{'type': 'mypush'}]
        self.assertEqual([{'type': 'mypush'}], push.message_config)

    def test_properties_can_be_set_while_checked_out(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        with checked_out(content) as co:
            push = IPushMessages(co)
            push.message_config = [{'type': 'mypush'}]
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        self.assertEqual([{'type': 'mypush'}], push.message_config)
        # These DAV properties are not serialized to XML.
        self.assertNotIn('mypush', zeit.cms.testing.xmltotext(content.xml))


class SendingNotifications(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        self.notifier = mock.Mock()
        zope.component.getGlobalSiteManager().registerAdapter(
            self.notifier,
            (zeit.cms.content.interfaces.ICommonMetadata,),
            zeit.push.interfaces.IMessage,
            name='mypush',
        )
        # getAdapter instantiates factory, which causes one call
        self.notifier = self.notifier()
        self.notifier.type = 'mypush'

    def test_enabled_service_is_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.message_config = [{'type': 'mypush', 'enabled': True}]
        IPublish(content).publish()
        self.assertTrue(self.notifier.send.called)

    def test_disabled_service_is_not_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.message_config = [{'type': 'mypush', 'enabled': False}]
        IPublish(content).publish()
        self.assertFalse(self.notifier.send.called)

    def test_error_during_push_is_caught(self):
        self.notifier.send.side_effect = RuntimeError('provoked')
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.message_config = [{'type': 'mypush', 'enabled': True}]
        IPublish(content).publish()
        # This is sort of assertNothingRaised, except that publishing
        # runs in a separate thread (remotetask), so we would not see
        # the exception here anyway.
        log = list(zeit.objectlog.interfaces.ILog(content).get_log())
        self.assertStartsWith('Error while sending', log[-1].message)
