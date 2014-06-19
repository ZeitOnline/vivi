import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.interfaces


class SocialFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.LAYER

    def get_article(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                return zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'online/2007/01/Somalia/@@edit.form.social?show_form=1')

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

        self.open_form()
        self.assertTrue(b.getControl('Enable Twitter').selected)
        self.assertTrue(b.getControl('Enable Facebook', index=0).selected)
        self.assertTrue(b.getControl('Enable Facebook Magazin').selected)

        b.getControl('Enable Twitter').selected = False
        b.getControl('Enable Facebook', index=0).selected = False
        b.getControl('Enable Facebook Magazin').selected = False
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
