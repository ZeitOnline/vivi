import zeit.cms.testing
import zeit.push.interfaces
import zeit.push.testing


class SocialFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(SocialFormTest, self).setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'testcontent/@@checkout')

    def get_article(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                return zeit.cms.interfaces.ICMSWCContent(
                    'http://xml.zeit.de/testcontent')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'testcontent/@@edit-social.html')

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
        b.getControl('Additional Twitter').displayValue = ['Wissen']
        b.getControl('Enable Facebook', index=0).selected = True
        b.getControl('Facebook Main Text').value = 'fb-main'
        b.getControl('Enable Facebook Magazin').selected = True
        b.getControl('Facebook Magazin Text').value = 'fb-magazin'
        b.getControl('Enable mobile push').selected = True
        b.getControl('Mobile title').value = 'mobile'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': True,
             'account': 'twitter_ressort_wissen'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-test',
             'override_text': 'fb-main'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-magazin',
             'override_text': 'fb-magazin'},
            push.message_config)
        self.assertIn(
            {'type': 'parse', 'enabled': True, 'override_text': 'mobile',
             'channels': zeit.push.interfaces.PARSE_NEWS_CHANNEL},
            push.message_config)

        self.open_form()
        self.assertTrue(b.getControl('Enable Twitter', index=0).selected)
        self.assertTrue(b.getControl('Enable Twitter Ressort').selected)
        self.assertTrue(b.getControl('Enable Facebook', index=0).selected)
        self.assertTrue(b.getControl('Enable Facebook Magazin').selected)
        self.assertTrue(b.getControl('Enable mobile push').selected)

        b.getControl('Enable Twitter', index=0).selected = False
        b.getControl('Enable Twitter Ressort').selected = False
        b.getControl('Enable Facebook', index=0).selected = False
        b.getControl('Enable Facebook Magazin').selected = False
        b.getControl('Enable mobile push').selected = False
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual(5, len(push.message_config))
        self.assertIn(
            {'type': 'twitter', 'enabled': False, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'twitter', 'enabled': False,
             'account': 'twitter_ressort_wissen'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': False, 'account': 'fb-test',
             'override_text': 'fb-main'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': False, 'account': 'fb-magazin',
             'override_text': 'fb-magazin'},
            push.message_config)
        self.assertIn(
            {'type': 'parse', 'enabled': False, 'override_text': 'mobile',
             'channels': 'parse-channel-news'},
            push.message_config)

        self.open_form()
        self.assertFalse(b.getControl('Enable Twitter', index=0).selected)
        self.assertFalse(b.getControl('Enable Twitter Ressort').selected)
        self.assertFalse(b.getControl('Enable Facebook', index=0).selected)
        self.assertFalse(b.getControl('Enable Facebook Magazin').selected)
        self.assertFalse(b.getControl('Enable mobile push').selected)

    def test_converts_ressorts_to_message_config(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Twitter Ressort').selected = True
        b.getControl('Additional Twitter').displayValue = ['Wissen']
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'enabled': True,
             'account': 'twitter_ressort_wissen'},
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
        for service in push.message_config:
            if (service['type'] != 'facebook'
                or service.get('account') != 'fb-test'):
                continue
            self.assertEqual('facebook', service['override_text'])
            break
        else:
            self.fail('facebook message_config is missing')
        self.open_form()
        self.assertEqual('facebook', b.getControl('Facebook Main Text').value)

    def test_stores_facebook_magazin_override_text(self):
        self.open_form()
        b = self.browser
        b.getControl('Facebook Magazin Text').value = 'facebook'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        for service in push.message_config:
            if (service['type'] != 'facebook'
                or service.get('account') != 'fb-magazin'):
                continue
            self.assertEqual('facebook', service['override_text'])
            break
        else:
            self.fail('facebook message_config is missing')
        self.open_form()
        self.assertEqual(
            'facebook', b.getControl('Facebook Magazin Text').value)

    def test_shows_long_text_as_bbb_for_facebook_override_text(self):
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        push.long_text = 'facebook'
        self.open_form()
        b = self.browser
        self.assertEqual(
            'facebook', b.getControl('Facebook Main Text').value)
        self.assertEqual(
            'facebook', b.getControl('Facebook Magazin Text').value)

    def test_stores_mobile_override_text(self):
        self.open_form()
        b = self.browser
        b.getControl('Mobile title').value = 'mobile'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        for service in push.message_config:
            if service['type'] != 'parse':
                continue
            self.assertEqual('mobile', service['override_text'])
            break
        else:
            self.fail('parse message_config is missing')
        self.open_form()
        self.assertEqual('mobile', b.getControl('Mobile title').value)


class SocialAddFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def test_applies_push_configuration_to_added_object(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/repository/@@zeit.cms.testcontenttype.AddSocial')
        b.getControl('File name').value = 'social'
        b.getControl('Title').value = 'Social content'
        b.getControl('Ressort', index=0).displayValue = ['Deutschland']
        b.getControl('Enable Twitter', index=0).selected = True
        b.getControl(name='form.actions.add').click()
        with zeit.cms.testing.site(self.getRootFolder()):
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/social')
            push = zeit.push.interfaces.IPushMessages(content)
            self.assertIn(
                {'type': 'twitter', 'enabled': True,
                 'account': 'twitter-test'}, push.message_config)


class TwitterShorteningTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.push.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(TwitterShorteningTest, self).setUp()
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.open(s.getLocation().replace('edit', 'edit-social'))

    def test_short_text_is_truncated_with_ellipsis(self):
        input = 'form.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 105 + ' This is too long'
        s.type(input, original + '\n')
        text = s.getValue(input)
        self.assertEqual(116, len(text))
        self.assertTrue(text.endswith('This is...'))

    def test_short_text_is_left_alone_if_below_limit(self):
        input = 'form.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 99 + ' This is not long'
        s.type(input, original + '\n')
        self.assertEqual(original, s.getValue(input))
