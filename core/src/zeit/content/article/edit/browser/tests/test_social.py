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

    def test_smoke_form_submit_stores_values(self):
        self.open_form()
        b = self.browser
        b.getControl('Push after next publish?').selected = True
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertEqual(True, push.enabled)
