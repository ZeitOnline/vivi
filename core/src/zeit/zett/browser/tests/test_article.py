import zeit.content.article.testing
import zeit.zett.testing


class FacebookTest(zeit.zett.testing.BrowserTestCase):
    def get_article(self):
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        return list(wc.values())[0]

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser

    def test_smoke_form_submit_stores_values(self):
        article = zeit.content.article.testing.create_article()
        self.repository['zett']['article'] = article
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository' '/zett/article/@@checkout')
        b.open('@@edit.form.social?show_form=1')
        self.assertFalse(b.getControl('Enable Facebook ze.tt').selected)
        b.getControl('Enable Facebook ze.tt').selected = True
        b.getControl('Facebook ze.tt Text').value = 'zett'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-zett', 'override_text': 'zett'},
            push.message_config,
        )
