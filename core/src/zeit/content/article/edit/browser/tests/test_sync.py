from selenium.webdriver.common.keys import Keys
import zeit.content.article.edit.browser.testing


class Supertitle(zeit.content.article.edit.browser.testing.EditorTestCase):

    supertitle = 'article-content-head.supertitle'
    teaser_supertitle = 'teaser-supertitle.teaserSupertitle'
    teaser_teaser = 'teaser-text.teaserText'
    tweet_main = 'social.short_text'
    genre_news = 'metadata-genre.genre'

    def setUp(self):
        super(Supertitle, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=%s' % self.teaser_supertitle)

    def test_teaser_supertitle_is_copied_to_article_supertitle_if_empty(self):
        s = self.selenium
        self.execute(
            'document.getElementById("%s").value = ""' % self.supertitle)
        s.click('//a[@href="edit-form-teaser"]')
        s.type('id=%s' % self.teaser_supertitle, 'super')
        s.keyPress('id=%s' % self.teaser_supertitle, Keys.TAB)
        # The sync triggers an inlineform save
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertValue('id=%s' % self.supertitle, 'super')

    def test_teaser_teaser_for_no_news_is_not_copied_to_twitter(self):
        s = self.selenium
        self.execute(
            'document.getElementById("%s").value = ""' % self.teaser_teaser)
        s.click('//a[@href="edit-form-teaser"]')
        s.type('id=%s' % self.teaser_teaser, 'teaser and tweet')
        s.keyPress('id=%s' % self.teaser_teaser, Keys.TAB)
        # The sync triggers an inlineform save
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertValue('id=%s' % self.tweet_main, '')
        s.assertAttribute('css=#social\\.short_text @style',
                          'color: rgb(153, 204, 153);')

    def test_teaser_teaser_for_news_is_copied_to_twitter_main_with_color(self):
        s = self.selenium
        s.click('id=edit-form-metadata')
        s.click('id=metadata-genre.genre')
        s.click('//option[@value="65199f22690d5ad5313ff54f56c1d8cb"]')
        # XXX This is tricky, but we somehow need to lose focus on the whole
        # widget and blur does not work this time. Maybe there is another way?
        s.clickAt('id=metadata-genre.genre', '-20,0')
        self.execute(
            'document.getElementById("%s").value = ""' % self.teaser_teaser)
        s.click('//a[@href="edit-form-teaser"]')
        s.type('id=%s' % self.teaser_teaser, 'teaser and tweet')
        s.keyPress('id=%s' % self.teaser_teaser, Keys.TAB)
        # The sync triggers an inlineform save
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertValue('id=%s' % self.tweet_main, 'teaser and tweet')
        s.assertAttribute('css=#social\\.short_text @style',
                          'color: rgb(153, 204, 153);')

    def test_main_twitter_color_changes_with_changing_checkbox(self):
        s = self.selenium
        s.click('//a[@href="edit-form-socialmedia"]')
        s.assertAttribute('css=#social\\.short_text @style',
                          'color: rgb(153, 204, 153);')
        s.click('id=social.twitter_main_enabled')
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertAttribute('css=#social\\.short_text @style',
                          'color: rgb(0, 0, 0);')
        s.click('id=social.twitter_main_enabled')
