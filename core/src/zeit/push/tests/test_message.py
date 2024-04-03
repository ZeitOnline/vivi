import zope.component
import zope.schema

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.push.interfaces
import zeit.push.testing


class MessageTest(zeit.push.testing.TestCase):
    def create_content(self, short_text=None):
        content = ExampleContentType()
        if short_text is not None:
            push = zeit.push.interfaces.IPushMessages(content)
            push.short_text = 'mytext'
        self.repository['foo'] = content
        return self.repository['foo']

    def test_mobile_is_separate_from_author(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = (
            {
                'type': 'mobile',
                'enabled': True,
                'variant': 'automatic-author',
                'payload_template': 'authors.json',
            },
        )
        data = zeit.push.interfaces.IAccountData(content)
        self.assertFalse(data.mobile_enabled)

    def test_mobile_bbb_compat_recognizes_without_variant(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = (
            {
                'type': 'mobile',
                'enabled': True,
                'override_text': 'mobile',
                'payload_template': 'foo.json',
            },
        )
        data = zeit.push.interfaces.IAccountData(content)
        self.assertEqual('mobile', data.mobile_text)

    def test_mobile_bbb_compat_adds_variant_on_write(self):
        content = self.create_content('mytext')
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = (
            {
                'type': 'mobile',
                'enabled': True,
                'override_text': 'mobile',
                'title': 'mobile title',
                'uses_image': False,
                'payload_template': 'foo.json',
            },
        )
        data = zeit.push.interfaces.IAccountData(content)
        data.mobile_payload_template = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/data/urbanairship-templates/eilmeldung.json'
        )
        self.assertEqual(
            (
                {
                    'type': 'mobile',
                    'enabled': True,
                    'override_text': 'mobile',
                    'title': 'mobile title',
                    'uses_image': False,
                    'variant': 'manual',
                    'payload_template': 'eilmeldung.json',
                },
            ),
            push.message_config,
        )

    def test_accountdata_validation_raises_error(self):
        content = self.create_content('mytext')
        data = zeit.push.interfaces.IAccountData(content)
        data.facebook_main_enabled = True
        errors = zope.schema.getSchemaValidationErrors(zeit.push.interfaces.IAccountData, data)
        assert errors == [
            ('facebook_main_text', zope.schema.interfaces.RequiredMissing('facebook_main_text'))
        ]

        data.facebook_main_enabled = False
        errors = zope.schema.getSchemaValidationErrors(zeit.push.interfaces.IAccountData, data)
        assert not errors
