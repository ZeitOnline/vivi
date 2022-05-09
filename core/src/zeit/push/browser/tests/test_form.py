from selenium.webdriver.common.keys import Keys
import zeit.cms.workingcopy.interfaces
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.workflow


class SocialFormTest(zeit.push.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'testcontent/@@checkout')

    def get_article(self):
        return zeit.cms.interfaces.ICMSWCContent(
            'http://xml.zeit.de/testcontent')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'testcontent/@@edit-social.html')
        self.browser.getControl('Payload Template').displayValue = ['Foo']

    def test_stores_IPushMessage_fields(self):
        self.open_form()
        b = self.browser
        b.getControl('Short push text').value = 'shorttext'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual('shorttext', push.short_text)

    def test_converts_account_checkboxes_to_message_config(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Twitter', index=0).selected = True
        b.getControl('Enable Twitter Ressort').selected = True
        b.getControl('Enable Twitter Print').selected = True
        b.getControl('Additional Twitter').displayValue = ['Wissen']
        b.getControl('Ressort Tweet').value = 'additional ressort tweet'
        b.getControl('Print Tweet').value = 'additional print tweet'
        b.getControl('Enable Facebook', index=0).selected = True
        b.getControl('Facebook Main Text').value = 'fb-main'
        b.getControl('Enable mobile push').selected = True
        b.getControl('Mobile title').value = 'mobile title'
        b.getControl('Mobile text').value = 'mobile'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        # No entries for Facebook Magazin and Campus are created, since they
        # are not included in the base form.
        self.assertEqual(5, len(push.message_config))
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'variant': 'ressort',
             'account': 'twitter_ressort_wissen',
             'override_text': 'additional ressort tweet'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'account': 'twitter-print',
             'override_text': 'additional print tweet'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-test',
             'override_text': 'fb-main'},
            push.message_config)
        self.assertIn(
            {'type': 'mobile', 'enabled': True, 'override_text': 'mobile',
             'title': 'mobile title', 'uses_image': False, 'variant': 'manual',
             'payload_template': 'foo.json'},
            push.message_config)

        self.open_form()
        self.assertTrue(b.getControl('Enable Twitter', index=0).selected)
        self.assertTrue(b.getControl('Enable Twitter Ressort').selected)
        self.assertTrue(b.getControl('Enable Twitter Print').selected)
        self.assertTrue(b.getControl('Enable Facebook', index=0).selected)
        self.assertTrue(b.getControl('Enable mobile push').selected)

        b.getControl('Enable Twitter', index=0).selected = False
        b.getControl('Enable Twitter Ressort').selected = False
        b.getControl('Enable Twitter Print').selected = False
        b.getControl('Enable Facebook', index=0).selected = False
        b.getControl('Enable mobile push').selected = False
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual(5, len(push.message_config))
        self.assertIn(
            {'type': 'twitter', 'enabled': False, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': False, 'variant': 'ressort',
             'account': 'twitter_ressort_wissen',
             'override_text': 'additional ressort tweet'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': False, 'account': 'twitter-print',
             'override_text': 'additional print tweet'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': False, 'account': 'fb-test',
             'override_text': 'fb-main'},
            push.message_config)
        self.assertIn(
            {'type': 'mobile', 'enabled': False, 'override_text': 'mobile',
             'title': 'mobile title', 'uses_image': False, 'variant': 'manual',
             'payload_template': 'foo.json'},
            push.message_config)

        self.open_form()
        self.assertFalse(b.getControl('Enable Twitter', index=0).selected)
        self.assertFalse(b.getControl('Enable Twitter Ressort').selected)
        self.assertFalse(b.getControl('Enable Twitter Print').selected)
        self.assertFalse(b.getControl('Enable Facebook', index=0).selected)
        self.assertFalse(b.getControl('Enable mobile push').selected)

    def test_converts_ressorts_to_message_config(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Twitter Ressort').selected = True
        b.getControl('Additional Twitter').displayValue = ['Wissen']
        b.getControl('Ressort Tweet').value = 'additional ressort tweet'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'variant': 'ressort',
             'account': 'twitter_ressort_wissen',
             'override_text': 'additional ressort tweet'},
            push.message_config)

        self.open_form()
        self.assertEqual(
            ['Wissen'], b.getControl('Additional Twitter').displayValue)

    def test_ressort_is_required_when_enabled(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Twitter Ressort').selected = True
        b.getControl('Apply').click()
        self.assertEllipsis(
            '...Additional Twitter...Required input is missing...', b.contents)

    def test_stores_facebook_main_override_text(self):
        self.open_form()
        b = self.browser
        b.getControl('Facebook Main Text').value = 'facebook'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='facebook', account='fb-test')
        self.assertEqual('facebook', service['override_text'])
        self.open_form()
        self.assertEqual('facebook', b.getControl('Facebook Main Text').value)

    def test_stores_mobile_override_text(self):
        self.open_form()
        b = self.browser
        b.getControl('Mobile title').value = 'mobile title'
        b.getControl('Mobile text').value = 'mobile'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile')
        self.assertEqual('mobile', service['override_text'])
        self.open_form()
        self.assertEqual('mobile', b.getControl('Mobile text').value)

    def test_stores_mobile_image(self):
        self.open_form()
        b = self.browser
        b.getControl('Mobile image').value = (
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile')
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG', service['image'])

        self.open_form()
        b.getControl('Mobile image').value = ''
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile')
        self.assertEqual(None, service['image'])

    def test_stores_mobile_buttons(self):
        self.open_form()
        b = self.browser
        b.getControl('Mobile buttons').displayValue = ['Share']
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile')
        self.assertEqual('share', service['buttons'])

    def test_stores_payload_template(self):
        self.open_form()
        b = self.browser
        b.getControl('Payload Template').displayValue = ['Foo']
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile')
        self.assertEqual('foo.json', service['payload_template'])

    def test_payload_template_is_required_when_enabled(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable mobile push').selected = True
        b.getControl('Mobile text').value = 'foo'
        b.getControl('Payload Template').displayValue = []
        b.getControl('Apply').click()
        self.assertEllipsis(
            '...Payload Template...Required input is missing...', b.contents)
        b.getControl('Payload Template').displayValue = ['Foo']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.getControl('Enable mobile push').selected = False
        b.getControl('Payload Template').displayValue = []
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)


class SocialAddFormTest(SocialFormTest):

    layer = zeit.push.testing.WSGI_LAYER

    def test_applies_push_configuration_to_added_object(self):

        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/repository/@@zeit.cms.testcontenttype.AddSocial')
        b.getControl('File name').value = 'social'
        b.getControl('Title').value = 'Social content'
        b.getControl('Ressort', index=0).displayValue = ['Deutschland']
        b.getControl('Enable Twitter', index=0).selected = True
        b.getControl('Payload Template').displayValue = ['Foo']
        b.getControl(name='form.mobile_enabled').value = False
        b.getControl(name='form.actions.add').click()
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/social')
        push = zeit.push.interfaces.IPushMessages(content)
        self.assertIn(
            {'type': 'twitter', 'enabled': True,
             'account': 'twitter-test'}, push.message_config)


class TwitterShorteningTest(zeit.push.testing.SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.open(s.getLocation().replace('edit', 'edit-social'))

    def test_short_text_is_truncated_with_ellipsis(self):
        input = 'form.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 245 + ' This is too long'
        s.type(input, original)
        # XXX Why does type('\t') not trigger `change` event anymore?
        self.execute('window.jQuery("#form\\\\.short_text").trigger("change")')
        text = s.getValue(input)
        self.assertEqual(256, len(text))
        self.assertTrue(text.endswith('This is...'))

    def test_short_text_is_left_alone_if_below_limit(self):
        input = 'form.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 239 + ' This is not long'
        s.type(input, original)
        s.keyPress(input, Keys.TAB)
        self.assertEqual(original, s.getValue(input))


class AuthorPushTest(zeit.push.testing.BrowserTestCase):

    def get_article(self):
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
        return list(wc.values())[0]

    def test_author_push_is_enabled_on_article_creation(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/')
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual(
            {'type': 'mobile',
             'payload_template': 'authors.json',
             'variant': 'automatic-author',
             'enabled': True},
            push.messages[0].config)
