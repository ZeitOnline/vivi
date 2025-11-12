import transaction
import zope.component
import zope.event

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.checkout.helper
import zeit.cms.content.interfaces
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship


class PayloadSourceTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        zeit.push.testing.create_payload_template()
        self.templates = list(zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE)

    def test_getValues_returns_all_templates_as_text_objects(self):
        # Change this if we decide we want a new
        # content type PaylaodTemplate
        self.assertTrue(1, len(self.templates))
        self.assertTrue(zeit.content.text.text.Text, type(self.templates[0]))

    def test_getTitle_returns_capitalized_title(self):
        self.assertTrue(
            'Template',
            zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.getTitle(self.templates[0]),
        )

    def test_getToken_returns_template_name(self):
        self.assertTrue(
            'template.json',
            zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.getToken(self.templates[0]),
        )

    def test_find_returns_correct_template(self):
        template_name = 'template.json'
        result = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory.find(template_name)
        self.assertEqual(template_name, result.__name__)


class MessageTest(zeit.push.testing.TestCase):
    name = 'mobile'

    def create_content(self, with_authors=False, **kw):
        """Create content with values given in arguments."""
        content = ExampleContentType()
        for key, value in kw.items():
            setattr(content, key, value)
        if with_authors:
            shakespeare = zeit.content.author.author.Author()
            shakespeare.firstname = 'William'
            shakespeare.lastname = 'Shakespeare'
            shakespeare.enable_followpush = True
            bacon = zeit.content.author.author.Author()
            bacon.firstname = 'Francis'
            bacon.lastname = 'Bacon'
            self.repository['shakespeare'] = shakespeare
            self.repository['bacon'] = bacon
            shakespeare.enable_followpush = False
            content.authorships = [
                content.authorships.create(self.repository['shakespeare']),
                content.authorships.create(self.repository['bacon']),
            ]
        self.repository['content'] = content
        return self.repository['content']

    def test_provides_image_url_if_image_is_referenced(self):
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config['image'] = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        self.assertEqual('http://img.zeit.de/2006/DSC00109_2.JPG', message.image_url)

    def test_message_text_favours_override_text_over_title(self):
        message = zope.component.getAdapter(
            self.create_content(title='nay'), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config = {'override_text': 'yay'}
        self.assertEqual('yay', message.text)

    def test_changes_to_template_are_applied_immediately(self):
        message = zeit.push.urbanairship.Message(self.repository['testcontent'])
        zeit.push.testing.create_payload_template('{"messages": {"one": 1}}', 'foo.json')
        transaction.commit()
        message.config['payload_template'] = 'foo.json'
        self.assertEqual({'one': 1}, message.render())
        zeit.push.testing.create_payload_template('{"messages": {"two": 1}}', 'foo.json')
        transaction.commit()
        self.assertEqual({'two': 1}, message.render())

    def test_payload_loads_jinja_payload_variables(self):
        template_content = """{"messages":[{
            "title": "{{article.title}}",
            "message": "{%if not uses_image %}Bildß{% endif %}"
        }]}"""
        zeit.push.testing.create_payload_template(template_content, 'bar.json')
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        message.config['payload_template'] = 'bar.json'
        payload = message.render()
        self.assertEqual('Bildß', payload[0].get('message'))
        self.assertEqual(message.context.title, payload[0].get('title'))

    def test_deep_link_starts_with_app_identifier(self):
        message = zope.component.getAdapter(
            self.create_content(), zeit.push.interfaces.IMessage, name=self.name
        )
        self.assertStartsWith(message.app_link, 'zeitapp://content')


class ChannelsTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        content = ExampleContentType()
        content.title = 'content_title'
        self.repository['content'] = content
        self.content = self.repository['content']

        for name in ['coffee', 'cake']:
            zeit.push.testing.create_payload_template(
                '{"messages": {"sweets": 42}}', f'{name}.json'
            )
            template = self.repository['data']['urbanairship-templates'][f'{name}.json']
            with zeit.cms.checkout.helper.checked_out(template) as co:
                co.channels = (('Push', name),)

    def message_config(self, name, enabled=True, template_type='mobile'):
        return {
            'enabled': enabled,
            'payload_template': f'{name}.json',
            'type': template_type,
        }

    def test_template_sets_content_channels(self):
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co.channels = (('Politik', None),)
        transaction.commit()
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (self.message_config('coffee'),)
        self.content = self.repository['content']
        self.assertIn(('Push', 'coffee'), self.content.channels)
        self.assertIn(('Politik', None), self.content.channels)

    def test_multiple_templates_add_multiple_channels(self):
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (
                self.message_config('coffee'),
                self.message_config('cake'),
            )

        self.assertIn(('Push', 'coffee'), self.content.channels)
        self.assertIn(('Push', 'cake'), self.content.channels)

    def test_must_not_add_channels_twice(self):
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co.channels = (('Push', 'coffee'),)
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (self.message_config('coffee'),)

        self.assertEqual((('Push', 'coffee'),), self.content.channels)

    def test_no_channel_template_does_not_break(self):
        zeit.push.testing.create_payload_template('{"messages": {"sweets": 42}}', 'cookies.json')
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co.channels = (('Politik', None),)
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (self.message_config('cookies'),)

        self.assertEqual((('Politik', None),), self.content.channels)

    def test_only_mobile_templates_allowed(self):
        zeit.push.testing.create_payload_template('{"messages": {"sweets": 42}}', 'not_mobile.json')
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (self.message_config('not_mobile', template_type='stone'),)
        self.assertEqual((), self.content.channels)

    def test_disabled_push_does_not_add_channel(self):
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.message_config = (self.message_config('cake', False),)
        self.assertEqual((), self.content.channels)
