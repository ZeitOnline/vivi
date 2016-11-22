import zeit.campus.testing
import zeit.cms.testing
import zeit.content.article.testing


class StudyCourseTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.campus.testing.LAYER

    def test_study_course_can_be_edited(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['campus']['article'] = (
                    zeit.content.article.testing.create_article())
                co = zeit.cms.checkout.interfaces.ICheckoutManager(
                    self.repository['campus']['article']).checkout()
                body = zeit.content.article.edit.interfaces.IEditableBody(co)
                block = body.create_item('studycourse')
                block.__name__ = 'blockname'
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/article'
            '/editable-body/blockname/@@edit-studycourse?show_form=1')
        self.assertEqual(
            ['Sonstiges'], b.getControl('Study course').displayValue)
        b.getControl('Study course').displayValue = ['Mathematik']
        b.getControl('Apply').click()
        b.open('@@edit-studycourse?show_form=1')
        self.assertEqual(
            ['Mathematik'], b.getControl('Study course').displayValue)


class FacebookTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.campus.testing.LAYER

    def get_article(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                return list(wc.values())[0]

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser

    def test_smoke_form_submit_stores_values(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.content.article.testing.create_article()
                self.repository['campus']['article'] = article
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository'
            '/campus/article/@@checkout')
        b.open('@@edit.form.social?show_form=1')
        self.assertFalse(b.getControl('Enable Facebook Campus').selected)
        b.getControl('Enable Facebook Campus').selected = True
        b.getControl('Facebook Campus Text').value = 'campus'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-campus',
             'override_text': 'campus'}, push.message_config)
