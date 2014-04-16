import zeit.content.article.edit.browser.testing


class KeywordSuggestions(
        zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(KeywordSuggestions, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent(
            'id=article-content-suggest-keywords')

    def test_button_toggles_suggestions(self):
        s = self.selenium
        s.assertText(
            'css=#article-content-suggest-keywords .ressort_keywords', '*qux*')
        s.assertVisible(
            'css=#article-content-suggest-keywords .ressort_keywords')
        s.click('css=#article-content-suggest-keywords .toggle_infos')
        s.waitForNotVisible(
            'css=#article-content-suggest-keywords .ressort_keywords')
        s.waitForVisible(
            'css=#article-content-suggest-keywords .all_keywords')

    def test_changing_ressort_reloads_suggestions(self):
        s = self.selenium
        input_ressort = 'metadata-a.ressort'
        s.select(input_ressort, 'label=Deutschland')
        s.fireEvent(input_ressort, 'blur')
        s.waitForText(
            'css=#article-content-suggest-keywords .ressort_keywords', '*foo*')
