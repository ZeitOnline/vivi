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
