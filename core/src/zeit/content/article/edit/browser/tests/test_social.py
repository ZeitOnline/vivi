import zeit.cms.testing
import zeit.content.article.testing


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

    def test_smoke_form_submit_stores_values(self):
        self.open_form()
        b = self.browser
        self.assertFalse(b.getControl('Enable Twitter', index=0).selected)
        b.getControl('Enable Twitter', index=0).selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'twitter', 'enabled': True, 'account': 'twitter-test'},
            push.message_config)
