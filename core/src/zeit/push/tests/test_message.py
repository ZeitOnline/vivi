from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublish
import zeit.push.interfaces
import zeit.push.testing
import zope.component
import zope.schema


class MessageTest(zeit.push.testing.TestCase):

    def create_content(self, short_text=None):
        content = ExampleContentType()
        if short_text is not None:
            push = zeit.push.interfaces.IPushMessages(content)
            push.short_text = 'mytext'
        self.repository['foo'] = content
        return self.repository['foo']

    def test_send_delegates_to_IPushNotifier_utility(self):
        content = self.create_content('mytext')
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='twitter')
        message.send()
        twitter = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='twitter')
        self.assertEqual(1, len(twitter.calls))
        call = twitter.calls[0]
        self.assertEqual('mytext', call[0])
        self.assertIn('http://www.zeit.de/foo', call[1])
        self.assertEqual({'message': message}, call[2])

    def test_no_text_configured_should_not_send(self):
        content = self.repository['testcontent']
        message = zope.component.getAdapter(
            content, zeit.push.interfaces.IMessage, name='twitter')
        with self.assertRaises(ValueError):
            message.send()
        twitter = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='twitter')
        self.assertEqual([], twitter.calls)

    def test_enabled_flag_is_removed_from_service_after_send(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({'type': 'twitter', 'enabled': True},)
        IPublish(content).publish()
        self.assertEqual(
            ({'type': 'twitter', 'enabled': False},), push.message_config)

    def test_twitter_ressort_bbb_compat_for_enabled(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'twitter', 'account': 'twitter_ressort_wissen'},)
        data = zeit.push.interfaces.IAccountData(content)
        data.twitter_ressort_enabled = True
        self.assertEqual(
            ({'type': 'twitter', 'variant': 'ressort',
              'account': 'twitter_ressort_wissen', 'enabled': True},),
            push.message_config)

    def test_twitter_ressort_bbb_compat_for_ressort(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'twitter', 'account': 'twitter_ressort_wissen',
            'enabled': True},)
        data = zeit.push.interfaces.IAccountData(content)
        data.twitter_ressort = 'twitter_ressort_politik'
        self.assertEqual(
            ({'type': 'twitter', 'variant': 'ressort',
              'account': 'twitter_ressort_politik', 'enabled': True},),
            push.message_config)

    def test_mobile_is_separate_from_author(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'mobile', 'enabled': True, 'variant': 'automatic-author',
            'payload_template': 'authors.json'},)
        data = zeit.push.interfaces.IAccountData(content)
        self.assertFalse(data.mobile_enabled)

    def test_mobile_bbb_compat_recognizes_without_variant(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'mobile', 'enabled': True, 'override_text': 'mobile',
            'payload_template': 'foo.json'},)
        data = zeit.push.interfaces.IAccountData(content)
        self.assertEqual('mobile', data.mobile_text)

    def test_mobile_bbb_compat_adds_variant_on_write(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = ({
            'type': 'mobile', 'enabled': True, 'override_text': 'mobile',
            'title': 'mobile title', 'uses_image': False,
            'payload_template': 'foo.json'},)
        data = zeit.push.interfaces.IAccountData(content)
        data.mobile_payload_template = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/data/urbanairship-templates/eilmeldung.json')
        self.assertEqual(({
            'type': 'mobile', 'enabled': True, 'override_text': 'mobile',
            'title': 'mobile title', 'uses_image': False, 'variant': 'manual',
            'payload_template': 'eilmeldung.json'},), push.message_config)

    def test_accountdata_validation_raises_error(self):
        content = self.create_content('mytext')
        data = zeit.push.interfaces.IAccountData(content)
        data.facebook_main_enabled = True
        errors = zope.schema.getSchemaValidationErrors(
            zeit.push.interfaces.IAccountData, data)
        assert errors == [
            ('facebook_main_text',
             zope.schema.interfaces.RequiredMissing('facebook_main_text'))]

        data.facebook_main_enabled = False
        errors = zope.schema.getSchemaValidationErrors(
            zeit.push.interfaces.IAccountData, data)
        assert not errors
