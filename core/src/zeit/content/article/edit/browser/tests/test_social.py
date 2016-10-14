import zeit.cms.testing
import zeit.content.article.edit.browser.testing
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


class SocialAMPTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(SocialAMPTest, self).setUp()
        self.add_article()

    def test_AMP_is_disabled_after_choosing_non_free_access(self):
        s = self.selenium
        s.click('css=#edit-form-socialmedia .fold-link')
        s.waitForVisible('css=#social\.is_amp')
        self.assertEqual(True, s.isEditable('css=#social\.is_amp'))

        s.check('css=#social\.is_amp')
        s.click('css=#edit-form-metadata .fold-link')
        s.waitForVisible('css=#form-metadata-access select')
        s.select('css=#form-metadata-access select', 'label=abopflichtig')
        s.type('css=#form-metadata-access select', '\t')
        # Autosave sometimes not triggered on Jenkins unless \t is typed twice
        try:
            s.waitForElementNotPresent('css=#form-metadata-access .dirty')
        except AssertionError:
            s.type('css=#form-metadata-access select', '\t')
        s.waitForElementNotPresent('css=#form-metadata-access .dirty')
        s.waitForElementPresent('css=.fieldname-is_amp .checkboxdisabled')
        self.assertEqual(False, s.isEditable('css=#social\.is_amp'))
