import zeit.campus.testing
import zeit.cms.testing
import zeit.content.article.testing


class StudyCourseTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.campus.testing.LAYER

    def test_study_course_can_be_edited(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.content.article.testing.create_article()
                self.repository['campus']['article'] = article
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository'
            '/campus/article/@@checkout')
        b.handleErrors = False
        b.open('@@edit.form.studycourse?show_form=1')
        self.assertEqual(
            ['Sonstiges'], b.getControl('Study course').displayValue)
        b.getControl('Study course').displayValue = ['Mathematik']
        b.getControl('Apply').click()
        b.open('@@edit.form.studycourse?show_form=1')
        self.assertEqual(
            ['Mathematik'], b.getControl('Study course').displayValue)
