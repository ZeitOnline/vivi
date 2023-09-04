import zeit.content.article.edit.browser.testing
import zeit.content.article.testing


class SocialFormTest(zeit.content.article.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'online/2007/01/Somalia/@@checkout')

    def get_article(self):
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


class MobileFormTest(zeit.content.article.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'online/2007/01/Somalia/@@checkout')

    def get_article(self):
        return zeit.cms.interfaces.ICMSWCContent(
            'http://xml.zeit.de/online/2007/01/Somalia')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'Somalia/@@edit.form.mobile?show_form=1')

    def test_sets_manual_flag_when_changing_image(self):
        self.open_form()
        b = self.browser
        b.getControl(name='mobile.mobile_image').value = (
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        b.getControl('Payload Template').displayValue = ['Foo']
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        service = push.get(type='mobile', variant='manual')
        self.assertEqual(
            'http://xml.zeit.de/2006/DSC00109_2.JPG', service['image'])
        self.assertEqual(True, service['image_set_manually'])

    def test_shows_notice_for_author_push(self):
        self.open_form()
        b = self.browser
        self.assertNotEllipsis(
            '...<div class="output">Author push enabled...', b.contents)
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        push.set({'type': 'mobile', 'variant': 'automatic-author'}, enabled=True)
        self.open_form()
        self.assertEllipsis(
            '...<div class="output">Author push enabled...', b.contents)
