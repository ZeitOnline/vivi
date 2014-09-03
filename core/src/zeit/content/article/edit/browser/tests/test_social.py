import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.interfaces


class SocialFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.LAYER

    def setUp(self):
        super(SocialFormTest, self).setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'online/2007/01/Somalia/@@checkout')

    def get_article(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                return zeit.cms.interfaces.ICMSWCContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'Somalia/@@edit.form.social?show_form=1')

    def test_stores_IPushMessage_fields(self):
        self.open_form()
        b = self.browser
        # b.getControl('Long push text').value = 'longtext'
        b.getControl('Short push text').value = 'shorttext'
        b.getControl('Push after next publish?').selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        # self.assertEqual('longtext', push.long_text)
        self.assertEqual('shorttext', push.short_text)
        self.assertEqual(True, push.enabled)

    def test_converts_account_checkboxes_to_message_config(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Twitter').selected = True
        b.getControl('Enable Facebook', index=0).selected = True
        b.getControl('Enable Facebook Magazin').selected = True
        # XXX temporarily disabled
        # b.getControl('Enable mobile push').selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-test'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-magazin'},
            push.message_config)
        # XXX temporarily disabled
        # self.assertIn(
        #     {'type': 'parse', 'enabled': True,
        #      'channels': 'parse-channel-news', 'title': 'News'},
        #     push.message_config)

        self.open_form()
        self.assertTrue(b.getControl('Enable Twitter').selected)
        self.assertTrue(b.getControl('Enable Facebook', index=0).selected)
        self.assertTrue(b.getControl('Enable Facebook Magazin').selected)
        # XXX temporarily disabled
        # self.assertTrue(b.getControl('Enable mobile push').selected)

        b.getControl('Enable Twitter').selected = False
        b.getControl('Enable Facebook', index=0).selected = False
        b.getControl('Enable Facebook Magazin').selected = False
        # XXX temporarily disabled
        # b.getControl('Enable mobile push').selected = False
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual(2, len(push.message_config))
        self.assertIn(
            {'type': 'twitter', 'enabled': False, 'account': 'twitter-test'},
            push.message_config)
        self.assertIn(
            {'type': 'facebook', 'enabled': False, 'account': 'fb-test'},
            push.message_config)

        self.open_form()
        self.assertFalse(b.getControl('Enable Twitter').selected)
        self.assertFalse(b.getControl('Enable Facebook', index=0).selected)
        self.assertFalse(b.getControl('Enable Facebook Magazin').selected)
        # XXX temporarily disabled
        # self.assertFalse(b.getControl('Enable mobile push').selected)

    def test_converts_ressorts_to_message_config(self):
        self.open_form()
        b = self.browser
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

    def test_checkbox_is_only_editable_while_checked_out(self):
        self.open_form()
        b = self.browser
        # Assert nothing raised
        b.getControl('Push after next publish?').selected = True

        b.open('@@checkin')
        b.open('@@edit.form.social?show_form=1')
        with self.assertRaises(AttributeError) as err:
            b.getControl('Push after next publish?').selected = True
        self.assertEqual('item is disabled', err.exception.message)

        b.open('@@checkout')
        b.open('@@edit.form.social?show_form=1')
        # Assert nothing raised
        b.getControl('Push after next publish?').selected = True


class TwitterShorteningTest(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_short_text_is_truncated_with_ellipsis(self):
        self.add_article()
        input = 'social.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 106 + ' This is too long'
        # XXX type() doesn't work with selenium-1 and FF>7
        self.eval(
            'document.getElementById("%s").value = "%s"' % (input, original))
        s.fireEvent(input, 'change')
        text = s.getValue(input)
        self.assertEqual(117, len(text))
        self.assertTrue(text.endswith('This is...'))

    def test_short_text_is_left_alone_if_below_limit(self):
        self.add_article()
        input = 'social.short_text'
        s = self.selenium
        s.waitForElementPresent(input)
        original = 'a' * 100 + ' This is not long'
        # XXX type() doesn't work with selenium-1 and FF>7
        self.eval(
            'document.getElementById("%s").value = "%s"' % (input, original))
        s.fireEvent(input, 'change')
        self.assertEqual(original, s.getValue(input))
