import urllib
import zeit.addcentral.testing
import zeit.cms.testing


class JavascriptTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.addcentral.testing.SELENIUM_LAYER

    def test_adding(self):
        s = self.selenium
        self.open('/')

        # provoke validation error
        s.waitForElementPresent('sidebar.form.type_')
        s.click('sidebar.form.actions.add')
        s.waitForElementPresent('xpath=//ul[@class="errors"]')

        # successful submit
        s.select('sidebar.form.type_', 'Image Group')
        s.select('sidebar.form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('sidebar.form.sub_ressort', 'Meinung')
        s.click('sidebar.form.actions.add')
        s.waitForLocation(
            '*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add*')

        # values should be remembered in the session
        s.waitForElementPresent('sidebar.form.ressort')
        s.assertSelectedLabel('sidebar.form.ressort', 'International')

        # but selecting something else should take preference
        s.select('sidebar.form.type_', 'Folder')
        s.click('sidebar.form.actions.add')
        s.waitForLocation(
            '*/international/meinung/*-*/@@zeit.cms.repository.folder.Add*')


class FormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.addcentral.testing.ZCML_LAYER

    def test_ressort_is_required_for_breaking_news(self):
        b = self.browser
        b.post('http://localhost/++skin++vivi/@@addcentral', urllib.urlencode({
            'sidebar.form.type_':
            '<zeit.content.article.interfaces.IBreakingNews>',
            'sidebar.form.ressort-empty-marker': '1',
            'sidebar.form.actions.add': 'Add'}))
        self.assertEllipsis('...Required input is missing...', b.contents)

        # Test that this does not poison the required status for other content
        # types.
        b.post('http://localhost/++skin++vivi/@@addcentral', urllib.urlencode({
            'sidebar.form.type_':
            'image',
            'sidebar.form.ressort-empty-marker': '1',
            'sidebar.form.actions.add': 'Add'}))
        self.assertEllipsis('...@@zeit.content.image.Add...', b.contents)
