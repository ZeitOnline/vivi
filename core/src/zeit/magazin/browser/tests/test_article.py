import zeit.cms.testing
import zeit.content.article.testing
import zeit.magazin.testing


class FacebookTest(zeit.magazin.testing.BrowserTestCase):
    def get_article(self):
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        return list(wc.values())[0]

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser

    def test_smoke_form_submit_stores_values(self):
        article = zeit.content.article.testing.create_article()
        self.repository['magazin']['article'] = article
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository' '/magazin/article/@@checkout')
        b.open('@@edit.form.social?show_form=1')
        self.assertFalse(b.getControl('Enable Facebook Magazin').selected)
        b.getControl('Enable Facebook Magazin').selected = True
        b.getControl('Facebook Magazin Text').value = 'magazin'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {
                'type': 'facebook',
                'enabled': True,
                'account': 'fb-magazin',
                'override_text': 'magazin',
            },
            push.message_config,
        )
