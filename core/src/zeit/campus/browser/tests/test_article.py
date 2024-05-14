import zeit.campus.testing
import zeit.content.article.testing


class StudyCourseTest(zeit.campus.testing.BrowserTestCase):
    def test_study_course_can_be_edited(self):
        self.repository['campus']['article'] = zeit.content.article.testing.create_article()
        co = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['campus']['article']
        ).checkout()
        body = zeit.content.article.edit.interfaces.IEditableBody(co)
        block = body.create_item('studycourse')
        block.__name__ = 'blockname'
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/article'
            '/editable-body/blockname/@@edit-studycourse?show_form=1'
        )
        self.assertEqual(['Sonstiges'], b.getControl('Study course').displayValue)
        b.getControl('Study course').displayValue = ['Mathematik']
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual(['Mathematik'], b.getControl('Study course').displayValue)


class FacebookTest(zeit.campus.testing.BrowserTestCase):
    def get_article(self):
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        return list(wc.values())[0]

    def test_smoke_form_submit_stores_values(self):
        article = zeit.content.article.testing.create_article()
        self.repository['campus']['article'] = article
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository' '/campus/article/@@checkout')
        b.open('@@edit.form.social?show_form=1')
        b.getControl('Facebook Campus Text').value = 'campus'
        b.getControl('Apply').click()
        article = self.get_article()
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {
                'type': 'facebook',
                'account': 'fb-campus',
                'override_text': 'campus',
            },
            push.message_config,
        )
