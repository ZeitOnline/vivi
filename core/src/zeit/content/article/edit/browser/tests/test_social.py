import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.interfaces


class SocialFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def get_article(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                return zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')

    def test_stores_IPushMessage_fields(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.social?show_form=1')
        b.getControl('Long push text').value = 'longtext'
        b.getControl('Short push text').value = 'shorttext'
        b.getControl('Push after next publish?').selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual('longtext', push.long_text)
        self.assertEqual('shorttext', push.short_text)
        self.assertEqual(True, push.enabled)

    def test_converts_account_checkboxes_to_message_config(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.social?show_form=1')
        b.getControl('Enable Facebook').selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn({'type': 'facebook'}, push.message_config)

        # XXX b.reload() does not work, why?
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.social?show_form=1')
        self.assertTrue(b.getControl('Enable Facebook').selected)

    def test_converts_twitter_ressort_to_message_config(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.social?show_form=1')
        b.getControl('Additional Twitter').displayValue = ['Wissen']
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'account': 'ressort_wissen'},
            push.message_config)

        # XXX b.reload() does not work, why?
        b.open('http://localhost/++skin++vivi/repository/'
               'online/2007/01/Somalia/@@edit.form.social?show_form=1')
        self.assertEqual(
            ['Wissen'], b.getControl('Additional Twitter').displayValue)
